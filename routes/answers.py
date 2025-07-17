from datetime import datetime

from pydantic import BaseModel
import pytz
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select, Session

from auth.authenticate import authenticate
from database.connection import get_session
from models import Answer
from models.answers import AnswerUpdate
from models.qa import QA
from utils.email import send_email
from utils.settings import settings

answer_router = APIRouter(
    tags=["Answer"],
)

class AnswerCreate(BaseModel):
    content: str
    qa_id: int


@answer_router.post("")
async def create_answer(new_answer: AnswerCreate, user: str = Depends(authenticate),
                        session=Depends(get_session)):
    if user != 'bsbus':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    raise_exception(new_answer.content, "Content cannot be blank")
    raise_exception(new_answer.qa_id, 'qa_id cannot be null')

    qa_statement = select(QA).where(QA.id == new_answer.qa_id)
    qa = session.exec(qa_statement).first()
    qa.done = True

    answer = Answer(
        content=new_answer.content,
        qa_id=new_answer.qa_id,
        creator=user,
        qa=qa,
    )

    session.add(qa)
    session.add(answer)
    session.commit()
    session.refresh(answer)

    # --- 이메일 발송 로직 추가 (Create) ---
    if qa.email: # QA 모델에 questioner_email 필드가 있다고 가정
        email_subject = f"문의하신 질문 '{qa.title[:30]}...'에 답변이 등록되었습니다."
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>안녕하세요, 백성운수(주) 입니다.</p>
            <br>
            
            <p>문의하신 질문에 대한 답변이 등록되었습니다.</p>
            <br>
            
            <p><strong>질문:</strong> {qa.title}</p>
            <br>
            
            <p>답변을 확인하시려면 아래 링크를 클릭해주세요:</p>
            <p><a href="{settings.bus_url}/qa/{qa.id}" style="display: inline-block; background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📝 답변 확인하러 가기</a></p>
            <br>
            
            <p>더 궁금한 점이 있으시면 언제든지 다시 문의해주세요.</p>
            <br>
            
            <p>감사합니다.</p>
            <br>
            
            <p><small>PS. 본 이메일은 자동으로 발송된 것입니다. 답변에 대한 추가 질문이 있으시면, 다시 문의해 주세요.</small></p>
        </body>
        </html>
        """
        email_sent = await send_email(qa.email, email_subject, email_body)
        if not email_sent:
            # 이메일 발송 실패 시 경고 또는 로그 남기기 (메인 로직은 성공으로 간주)
            print(f"Failed to send email to {qa.email}")
            # 또는 
            raise HTTPException(status_code=500, detail="Answer created, but failed to send notification email.")
    # -----------------------------------

    return {"message": "답변이 성공적으로 등록되었습니다.", "answer": answer}


@answer_router.delete("/{id}")
async def delete_answer(id: int, user: str = Depends(authenticate), session: Session = Depends(get_session)) -> dict:
    answer_exist = session.get(Answer, id)
    if answer_exist.creator != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You do not have permission to perform this action",
        )
    if answer_exist:
        qa = session.get(QA, answer_exist.qa_id)
        qa.done = False

        session.add(qa)
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
async def update_answer(id: int, update_answer: AnswerUpdate, user: str = Depends(authenticate),
                        session: Session = Depends(get_session)) -> Answer:
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

         # --- 이메일 발송 로직 추가 (Update) ---
        qa = session.get(QA, answer.qa_id)
        if qa and qa.email:
            email_subject = f"문의하신 질문 '{qa.title[:30]}...'에 대한 답변이 수정되었습니다."
            email_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <p>안녕하세요, 백성운수(주) 입니다.</p>
                <br>
                
                <p>문의하신 질문에 대한 답변이 수정되었습니다.</p>
                <br>
                
                <p><strong>질문:</strong> {qa.title}</p>
                <br>
                
                <p>수정된 답변을 확인하시려면 아래 링크를 클릭해주세요:</p>
                <p><a href="{settings.bus_url}/qa/{qa.id}" style="display: inline-block; background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📝 수정된 답변 확인하러 가기</a></p>
                <br>
                
                <p>더 궁금한 점이 있으시면 언제든지 다시 문의해주세요.</p>
                <br>
                
                <p>감사합니다.</p>
                <br>
                
                <p><small>PS. 본 이메일은 자동으로 발송된 것입니다. 답변에 대한 추가 질문이 있으시면, 다시 문의해 주세요.</small></p>
            </body>
            </html>
            """
            email_sent = await send_email(qa.email, email_subject, email_body)
            if not email_sent:
                print(f"Failed to send email to {qa.email} after update.")
        # -----------------------------------

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
