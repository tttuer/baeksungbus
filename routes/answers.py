from datetime import datetime

import pytz
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select, Session

from auth.authenticate import authenticate
from database.connection import get_session
from models import Answer
from models.answers import AnswerUpdate
from models.qa import QA

answer_router = APIRouter(
    tags=["Answer"],
)

@answer_router.post("/", response_model=Answer)
async def create_answer(new_answer: Answer, qa_id: int, user: str = Depends(authenticate), session=Depends(get_session)) -> Answer:
    raise_exception(new_answer.content, "Content cannot be blank")
    raise_exception(qa_id, 'qa_id cannot be null')

    qa_statement = select(QA).where(QA.id == qa_id)
    qa = session.exec(qa_statement).first()
    new_answer.qa = qa

    new_answer.creator = user
    new_answer.qa_id = qa_id

    session.add(new_answer)
    session.commit()
    session.refresh(new_answer)

    return new_answer


@answer_router.delete("/{id}")
async def delete_answer(id: int, user: str = Depends(authenticate), session: Session = Depends(get_session)) -> dict:
    answer_exist = session.get(Answer, id)
    if answer_exist.creator != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You do not have permission to perform this action",
        )
    if answer_exist:
        session.delete(answer_exist)
        session.commit()
        return {
            'message': 'Answer deleted',
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event not found",
    )

@answer_router.patch("/{id}")
async def update_answer(id: int, update_answer: AnswerUpdate, user: str = Depends(authenticate), session: Session = Depends(get_session)) -> Answer:
    answer = session.get(Answer, id)
    if answer.creator != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You do not have permission to perform this action",
        )
    if answer:
        answer_data = update_answer.model_dump(exclude_unset=True)
        for key, value in answer_data.items():
            setattr(answer, key, value)
        session.add(answer)
        session.commit()
        session.refresh(answer)

        return answer
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Answer not found",
    )

def raise_exception(val, message: str):
    if val == '' or not val:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

def get_kr_date():
    # KST 타임존을 설정
    kst = pytz.timezone('Asia/Seoul')

    # 현재 KST 날짜와 시간 가져오기
    return datetime.now(kst).strftime('%Y-%m-%d')

