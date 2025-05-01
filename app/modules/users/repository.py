import uuid
from typing import Sequence, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload # Se precisarmos carregar relacionamentos no futuro

from .models import User
from .schema import UserCreate, UserUpdate

# Nota: A lógica de hash de senha NÃO deve estar aqui.
# O repository recebe e salva os dados como estão. O Service prepara os dados.

async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    """Busca um usuário pelo seu ID."""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Busca um usuário pelo seu email."""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[User]:
    """Busca uma lista paginada de usuários."""
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc()) # Exemplo de ordenação
    )
    return result.scalars().all()

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Cria um novo usuário no banco de dados."""
    # Assume que user_in.password já é o hash! O hash deve ser feito no Service.
    db_user = User(
        email=user_in.email,
        password=user_in.password, # Salva a string recebida (espera-se hash)
        full_name=user_in.full_name
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user) # Atualiza o objeto db_user com dados do DB (como ID, created_at)
    return db_user

async def update_user(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    """Atualiza um usuário existente no banco de dados."""
    update_data = user_in.model_dump(exclude_unset=True) # Pega só os campos que foram enviados

    # Se a senha foi enviada no update, assume-se que já está hasheada pelo Service
    if "password" in update_data and update_data["password"]:
        update_data["password"] = update_data.pop("password")
    elif "password" in update_data:
         del update_data["password"] # Remove se for None ou vazio

    if not update_data:
        return db_user # Nenhum dado para atualizar

    # Atualiza os atributos do objeto SQLAlchemy existente
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user) # Adiciona o objeto modificado à sessão
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, db_user: User) -> None:
    """Remove um usuário do banco de dados."""
    await db.delete(db_user)
    await db.commit() 