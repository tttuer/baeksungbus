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
async def signup(user: User):
    user_exist = await User.find_one(User.id == user.id)
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Email already registered'
        )

    hashed_password = hash_password.create_hash(user.password)
    user.password = hashed_password
    await user_database.save(user)
    return {
        'message': 'User registered',
    }


@users_router.post('/signin', response_model=TokenResponse)
async def signin(user: OAuth2PasswordRequestForm = Depends()):
    if user.username != 'bsbus':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User is unauthorized user'
        )
    user_exist = await User.find_one(User.id == user.username)
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

    access_token = create_access_token(user_exist.email)
    return {
        'access_token': access_token,
        'token_type': 'Bearer'
    }