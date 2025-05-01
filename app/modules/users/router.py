import uuid
from typing import List # Import List for Python < 3.9 compatibility
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from . import schema as user_schema
from . import service as user_service

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/",
    response_model=user_schema.UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a new user (merchant/client) in the system.",
)
async def create_user_endpoint(
    user_in: user_schema.UserCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Cria um novo usuário.

    - **email**: Email único do usuário.
    - **password**: Senha (será hasheada).
    - **full_name**: Nome completo (opcional).
    """
    try:
        created_user = await user_service.create_user(db=db, user_in=user_in)
        return created_user
    except HTTPException as e:
        # Repassa exceções HTTP levantadas pelo serviço (ex: email duplicado)
        raise e
    except Exception as e:
        # Logar o erro e retornar um erro genérico
        # logger.error(f"Error creating user: {e}") # Adicionar logging real depois
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while creating the user.",
        )


# Endpoint para listar usuários
@router.get(
    "/",
    response_model=List[user_schema.UserPublic], # Retorna uma lista de usuários
    summary="Get a list of users",
)
async def get_users_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db_session),
):
    """Retorna uma lista paginada de usuários."""
    users = await user_service.get_users(db, skip=skip, limit=limit)
    return users


# Endpoint para buscar um usuário específico pelo ID
@router.get(
    "/{user_id}",
    response_model=user_schema.UserPublic,
    summary="Get a specific user by ID",
)
async def get_user_endpoint(
    user_id: uuid.UUID, # ID recebido na URL
    db: AsyncSession = Depends(get_db_session),
):
    """Busca e retorna um usuário pelo seu UUID."""
    db_user = await user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


# Endpoint para atualizar um usuário
@router.patch(
    "/{user_id}",
    response_model=user_schema.UserPublic,
    summary="Update a user",
)
async def update_user_endpoint(
    user_id: uuid.UUID,
    user_in: user_schema.UserUpdate, # Dados de atualização no corpo
    db: AsyncSession = Depends(get_db_session),
):
    """
    Atualiza parcialmente um usuário existente.
    Apenas os campos fornecidos no corpo da requisição serão atualizados.
    """
    try:
        updated_user = await user_service.update_user(db=db, user_id=user_id, user_in=user_in)
        return updated_user
    except HTTPException as e:
        # Repassa 404 ou outros erros do serviço
        raise e
    except Exception as e:
        # logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while updating the user.",
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
)
async def delete_user_endpoint(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """Deleta um usuário pelo seu UUID."""
    try:
        await user_service.delete_user(db=db, user_id=user_id)
        # Nenhum retorno aqui, pois o status é 204
    except HTTPException as e:
         # Repassa 404 do serviço
        raise e
    except Exception as e:
        # logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while deleting the user.",
        ) 