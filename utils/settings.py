from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kakao_api_key: str
    db_user: str
    db_password: str
    middleware_secret: str

    class Config:
        env_file = ".env"


settings = Settings()