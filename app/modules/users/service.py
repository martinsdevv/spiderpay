import uuid
from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.security import get_password_hash
from . import repository as user_repo # Alias para o repositório
from .models import User
from .schema import UserCreate, UserUpdate, UserPublic

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    Cria um novo usuário, fazendo o hash da senha antes de salvar.
    Levanta HTTPException se o email já existir.
    """
    db_user = await user_repo.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Gera o hash da senha
    hashed_password = get_password_hash(user_in.password)

    # Cria um objeto User model com os dados corretos (incluindo o hash)
    # O repositório espera o hash no campo 'password' do UserCreate, então adaptamos.
    # Uma abordagem alternativa seria refatorar o repositório para aceitar 'hashed_password'.
    user_data_for_repo = UserCreate(
        email=user_in.email,
        full_name=user_in.full_name,
        password=hashed_password # Passa o HASH para o campo password do schema de entrada
    )

    return await user_repo.create_user(db=db, user_in=user_data_for_repo)

async def get_user(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    """Busca um usuário pelo ID."""
    return await user_repo.get_user_by_id(db, user_id=user_id)

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Busca um usuário pelo email."""
    # Reutiliza a função do repositório diretamente
    return await user_repo.get_user_by_email(db, email=email)


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[User]:
    """Busca usuários com paginação."""
    return await user_repo.get_users(db, skip=skip, limit=limit)

async def update_user(
    db: AsyncSession, user_id: uuid.UUID, user_in: UserUpdate
) -> User:
    """
    Atualiza um usuário. Faz hash se uma nova senha for fornecida.
    Levanta HTTPException se o usuário não for encontrado.
    """
    db_user = await get_user(db, user_id=user_id) # Reutiliza a função get_user deste serviço
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prepara os dados para atualização
    update_data = user_in.model_dump(exclude_unset=True)

    # Se a senha está sendo atualizada, calcula o novo hash
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        # Coloca o hash no dicionário de dados para o repositório
        update_data["password"] = hashed_password
    elif "password" in update_data:
        del update_data["password"] # Remove se None ou vazio para não sobrescrever

    # Cria um objeto UserUpdate com os dados processados para passar ao repositório
    # (Adaptando à assinatura atual do repositório)
    user_update_for_repo = UserUpdate(**update_data)

    return await user_repo.update_user(db=db, db_user=db_user, user_in=user_update_for_repo)


async def delete_user(db: AsyncSession, user_id: uuid.UUID) -> None:
    """
    Deleta um usuário.
    Levanta HTTPException se o usuário não for encontrado.
    """
    db_user = await get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    await user_repo.delete_user(db=db, db_user=db_user) 