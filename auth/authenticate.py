from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.jwt_handler import verify_access_token, get_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/login')


async def authenticate(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Sign in for access',
        )

    decoded_token = get_access_token(token)
    if not decoded_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid token',
        )
    return decoded_token['user']


def check_admin(user: str):
    if user != 'bsbus':
        raise HTTPException(
            status_code=status.HTTP_AUTHORIZED,
            detail="Not authenticated",
        )


# 토큰을 검사하는 미들웨어
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # /adm에 접근할 때 /adm/login을 제외한 모든 경로에 대해 토큰 검증
        if request.url.path.startswith("/adm") and request.url.path != "/adm/login":
            token = request.session.get("access_token")

            # 토큰이 없거나 유효하지 않으면 로그인 페이지로 리다이렉트
            if not token or not verify_access_token(token):
                return RedirectResponse(url="/adm/login")

        # 유효한 토큰이면 요청 계속 진행
        return await call_next(request)
