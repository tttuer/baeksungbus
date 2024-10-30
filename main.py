from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from routes.answers import answer_router
from routes.notices import notice_router
from routes.qas import qa_router
from routes.users import users_router
from routes.pages import page_router
from routes.captcha_route import captcha_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
# 라우터 세팅
app.include_router(answer_router, prefix='/answers')
app.include_router(qa_router, prefix='/qas')
app.include_router(users_router, prefix='/users')
app.include_router(notice_router, prefix='/notices')
app.include_router(page_router)
app.include_router(captcha_router)

# 프론트 세팅
# 정적 파일 경로 설정
app.mount("/static", StaticFiles(directory="static"), name="static")



if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
