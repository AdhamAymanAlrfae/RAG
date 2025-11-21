from pydantic_settings import BaseSettings


class Config(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    FILE_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    class Config:
        env_file = ".env"


def get_config():
    return Config()
