from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import selectinload
from sqlmodel import select, Session

from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from database.connection import get_session
from models import Answer
from models.qa import QA, QAShort

from fastapi.responses import RedirectResponse
from fastapi import Query

from datetime import datetime
import pytz

from models.users import User, TokenResponse

users_router = APIRouter(
    tags=['User']
)

users = {}

hash_password = HashPassword()


@users_router.post('/signup')
async def signup(user: User, session: Session = Depends(get_session)):
    user_exist = session.get(User, user.id)

    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='ID already registered'
        )

    hashed_password = hash_password.create_hash(user.password)
    user.password = hashed_password

    session.add(user)
    session.commit()
    session.refresh(user)

    return {
        'message': 'User registered',
    }


@users_router.post('/login', response_model=TokenResponse)
async def signin(
    user: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
    next: str = Query("/", description="URL to redirect after login")  # next 파라미터 추가
):
    if user.username != 'bsbus':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User is unauthorized user'
        )
    user_exist = session.get(User, user.username)
    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='ID not registered'
        )
    if not hash_password.verify_password(user.password, user_exist.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Password mismatch'
        )

    access_token = create_access_token(user_exist.id)

    # 로그인 성공 후 next URL로 리다이렉트
    response = RedirectResponse(url=next, status_code=303)
    response.set_cookie(key="access_token", value=access_token)  # 액세스 토큰을 쿠키로 설정
    return response