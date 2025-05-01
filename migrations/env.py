import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Adicionar o diretório raiz do projeto ao sys.path
# para que possamos importar 'app'
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# Importar a Base e a URL do banco de dados das configurações da aplicação
from app.core.database import Base
from app.core.config import settings

# Importar modelos aqui para que o autogenerate funcione
from app.modules.users.models import User
# from app.modules.payments.models import Payment # Exemplo
# from app.modules.transactions.models import Transaction # Exemplo

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Obter a URL async da configuração
db_url_async = str(settings.DATABASE_URL)
# Criar uma URL síncrona substituindo o driver (se presente)
db_url_sync = db_url_async.replace("postgresql+asyncpg://", "postgresql://")
# Ou, mais explicitamente, forçar psycopg2:
# db_url_sync = db_url_async.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

# Definir a URL SÍNCRONA para o Alembic
config.set_main_option('sqlalchemy.url', db_url_sync)

# add your model's MetaData object here
# for 'autogenerate' support
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using a synchronous connection."""

    # Cria uma engine SÍNCRONA a partir da configuração no alembic.ini
    # (que agora tem a nossa DATABASE_URL).
    # SQLAlchemy 2.0 é inteligente o suficiente para usar um driver síncrono
    # (como psycopg2, que instalamos) se disponível, mesmo que a URL seja asyncpg.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Usa a engine síncrona para conectar
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        # Executa as migrações dentro de uma transação
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() # Chama a função síncrona diretamente
