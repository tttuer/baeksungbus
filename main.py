from contextlib import asynccontextmanager

import uvicorn

from routes.answers import answer_router
from routes.qas import qa_router
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from routes.users import users_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(answer_router, prefix='/answers')
app.include_router(qa_router, prefix='/qas')
app.include_router(users_router, prefix='/users')

# 세션 미들웨어 설정 (리다이렉트에 필요할 수 있음)
app.add_middleware(SessionMiddleware, secret_key="pRd8mpcYQaCBEW4S3Pl2GkyfE3JoTqwP")

# 커스텀 401 예외 핸들러
@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:  # 인증 실패 시
        # 현재 경로를 쿼리 파라미터로 추가
        return RedirectResponse(url=f"/login?next={request.url.path}", status_code=303)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
