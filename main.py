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


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
# 라우터 세팅
app.include_router(answer_router, prefix='/answers')
app.include_router(qa_router, prefix='/qas')
app.include_router(users_router, prefix='/users')
app.include_router(notice_router, prefix='/notices')

# 프론트 세팅
# 정적 파일 경로 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 디렉토리 설정
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 추가 경로 예시
@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})
@app.get("/schedule", response_class=HTMLResponse)
async def schedule(request: Request):
    return templates.TemplateResponse("schedule.html", {"request": request})
@app.get("/ddock", response_class=HTMLResponse)
async def ddock(request: Request):
    return templates.TemplateResponse("ddock.html", {"request": request})
@app.get("/location", response_class=HTMLResponse)
async def ddock(request: Request):
    return templates.TemplateResponse("location.html", {"request": request})

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
