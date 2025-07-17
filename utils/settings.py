from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str 
    middleware_secret: str
    docs_id: str
    docs_password: str
    email_username: str
    email_password: str
    email_server: str
    email_port: int


    class Config:
        env_file = ".env"


settings = Settings()