from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings
from collections.abc import AsyncGenerator as _AsyncGenerator_collections
from typing import AsyncGenerator

# Cria a engine assíncrona do SQLAlchemy usando a URL do banco de dados das configurações
async_engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    pool_pre_ping=True
)

# Cria uma fábrica de sessões assíncronas (sessionmaker) configurada
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()

# Dependência do FastAPI para obter uma sessão do banco de dados
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency para injetar uma AsyncSession do SQLAlchemy nas rotas."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            pass
