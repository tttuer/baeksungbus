from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from database.connection import get_session
from models.users import User, TokenResponse

users_router = APIRouter(
    tags=['User']
)

users = {}

hash_password = HashPassword()


@users_router.post('/signup')
async def signup(user: User, session=Depends(get_session)):
    user_exist = session.get(User, user.id)
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Email already registered'
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
async def login(response: Response, user: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)):
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

    # Authorization 헤더에 Bearer 토큰을 추가
    response.headers["Authorization"] = f"Bearer {access_token}"

    # 여전히 JSON 응답으로 토큰도 반환
    return {
        'access_token': access_token,
        'token_type': 'Bearer'
    }