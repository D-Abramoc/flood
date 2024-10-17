from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = 'Flood'
    description: str = 'Флудилка'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'
    algorithm: str = ''

    lifetime_seconds: int = 3000
    max_password_length: int = 3
    max_length_string: int = 100
    min_length_string: int = 1
    base_dir: Path = Path(__file__).parent.parent.parent

    host: str = 'localhost'
    model_config = SettingsConfigDict(env_file='infra/.env', extra='ignore')


class LoggerSettings(BaseSettings):
    HANDLERS: str = ''
    LOG_LEVEL: str = ''
    LOGGER_FILE_PATH: str = 'app/logs/app_logger.log'

    model_config = SettingsConfigDict(env_file='infra/.env', extra='ignore')


settings = Settings()
logger_settings = LoggerSettings()


def get_auth_data():
    return {
        'secret_key': settings.secret,
        'algorithm': settings.algorithm
    }
