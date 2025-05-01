from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, SecretStr
from typing import Literal, Union

class Settings(BaseSettings):
    """Carrega as configurações da aplicação a partir de variáveis de ambiente ou arquivo .env."""
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore' 
    )

    DATABASE_URL: Union[PostgresDsn, str]

    APP_NAME: str = "SpiderPay API"
    DEBUG: bool = False

    ACTIVE_GATEWAY: Literal["mock"] = "mock"

    SECRET_KEY: SecretStr

settings = Settings()
