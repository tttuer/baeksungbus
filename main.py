from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from routes.answers import answer_router
from routes.qas import qa_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(answer_router, prefix='/answers')
app.include_router(qa_router, prefix='/qas')

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
