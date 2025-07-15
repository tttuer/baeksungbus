from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_user: str
    db_password: str
    middleware_secret: str

    class Config:
        env_file = ".env"


settings = Settings()