from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from routes.answers import answer_router
from routes.notices import notice_router
from routes.qas import qa_router
from routes.users import users_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(answer_router, prefix='/answers')
app.include_router(qa_router, prefix='/qas')
app.include_router(users_router, prefix='/users')
app.include_router(notice_router, prefix='/notices')

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
