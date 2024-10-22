from fastapi import APIRouter, HTTPException, status

from models.users import User, UserSingIn

users_router = APIRouter(
    tags=['User']
)

users = {}


@users_router.post('/signup')
async def signup(data: User):
    if data.email in users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Email already registered'
        )
    users[data.email] = data
    return {
        'message': 'User registered',
    }


@users_router.post('/signin')
async def signin(user: UserSingIn):
    if user.email not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Email not registered'
        )
    if user.password != users[user.email].password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Password mismatch'
        )

    return {
        'message': 'User signed in successfully',
    }
