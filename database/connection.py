import os
from typing import Optional

from pydantic_settings import BaseSettings
from sqlmodel import Session, create_engine
from utils.settings import settings

# MySQL 데이터베이스 설정
# database_connection_string = 'mysql+mysqlconnector://test_user:test_user@localhost:3306/baeksung'
database_connection_string = f'mysql+mysqlconnector://{settings.db_user}:{settings.db_password}@{settings.db_host}:3306/baeksung'
# database_connection_string = f'mysql+mysqlconnector://{database_user}:{database_password}@localhost:3306/pyeongtaek'
engine_url = create_engine(database_connection_string, echo=True)


class Settings(BaseSettings):
    SECRET_KEY: Optional[str] = 'HI5HL3V3L$3CR3T'


def get_session():
    # 세션을 여는 함수
    with Session(engine_url) as session:
        yield session
