from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from auth.authenticate import AuthMiddleware
from routes.answers import answer_router
from routes.bus_schedules import schedule_router
from routes.captcha_route import captcha_router
from routes.ddocks import ddock_router
from routes.notices import notice_router
from routes.pages import page_router
from routes.qas import qa_router
from routes.users import users_router
from utils.settings import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Vue.js 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

# 라우터 세팅
# /api 기본 경로를 가지는 APIRouter 생성
api_router = APIRouter(prefix="/api")

# 모든 라우터에 /api 경로 적용
api_router.include_router(answer_router, prefix="/answers")
api_router.include_router(qa_router, prefix="/qas")
api_router.include_router(users_router, prefix="/users")
api_router.include_router(notice_router, prefix="/notices")
api_router.include_router(schedule_router, prefix="/schedules")
api_router.include_router(ddock_router, prefix="/ddocks")
api_router.include_router(captcha_router)

# api_router를 메인 애플리케이션에 추가
app.include_router(api_router)
app.include_router(captcha_router)
app.include_router(page_router)  # 프론트엔드 라우터는 /api가 필요 없으므로 그대로 추가

# 프론트 세팅
# 정적 파일 경로 설정

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.middleware_secret,  # settings에서 가져온 미들웨어 시크릿 키 사용
)
