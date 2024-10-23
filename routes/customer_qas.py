from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import selectinload, joinedload
from sqlmodel import select, Session

from database.connection import get_session
from models.customer_qa import CustomerQA, CustomerQAShort, CustomerQAWithAnswer
from models.events import Event, EventUpdate

from fastapi import Query

from datetime import datetime
import pytz

from models.answers import Answer

customer_qa_router = APIRouter(
    tags=["Customer_qa"],
)


@customer_qa_router.get("/", response_model=List[CustomerQAShort])
async def get_qas(
        page: int = Query(1, ge=1),  # 기본 페이지 번호는 1
        page_size: int = Query(20, ge=1, le=100),  # 페이지 크기는 1~100 사이, 기본 20
        session: Session = Depends(get_session)
) -> List[CustomerQAShort]:
    offset = (page - 1) * page_size  # 페이지 번호에 따른 오프셋 계산

    # 필요한 필드만 선택해서 가져오는 쿼리 작성
    statement = select(
        CustomerQA.id,
        CustomerQA.title,
        CustomerQA.writer,
        CustomerQA.c_date,
        CustomerQA.done,
        CustomerQA.read_cnt
    ).offset(offset).limit(page_size)

    # 실행하고 결과를 가져옴
    result = session.exec(statement).all()

    # 필요한 필드를 CustomerQAShort로 변환
    qas_short = [
        CustomerQAShort(
            id=row.id,
            title=row.title,
            writer=row.writer,
            c_date=row.c_date.strftime('%Y-%m-%d'),
            done=row.done,
            read_cnt=row.read_cnt
        ) for row in result
    ]

    return qas_short


@customer_qa_router.get("/{id}", response_model=CustomerQAWithAnswer, response_model_exclude={"password"})
async def get_qa(id: int, password: str, session: Session = Depends(get_session)) -> CustomerQAWithAnswer:
    # CustomerQA를 id로 조회하고 관련된 answers를 미리 로드
    statement = select(CustomerQA).options(joinedload(CustomerQA.answers)).where(CustomerQA.id == id)
    qa = session.exec(statement).first()

    if not qa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CustomerQA not found",
        )
    if qa.password != password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is not correct",
        )

    print(f'qa.answers: {qa.answers}')

    return qa


@customer_qa_router.post("/", response_model=CustomerQA)
async def create_customer_qa(new_qa: CustomerQA, session=Depends(get_session)) -> CustomerQA:
    raise_exception(new_qa.writer, "Writer cannot be blank")
    raise_exception(new_qa.password, "Password cannot be blank")
    raise_exception(new_qa.title, "Title cannot be blank")

    new_qa.c_date = get_kr_date()

    session.add(new_qa)
    session.commit()
    session.refresh(new_qa)

    return new_qa


@customer_qa_router.delete("/{id}")
async def delete_event(id: int, session: Session = Depends(get_session)) -> dict:
    event = session.get(Event, id)
    if event:
        session.delete(event)
        session.commit()
        return {
            'message': 'Event deleted',
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event not found",
    )


@customer_qa_router.delete("/")
async def delete_all_events() -> dict:
    return {
        'message': 'All event deleted',
    }


@customer_qa_router.put("/{id}")
async def update_event(id: int, update_event: EventUpdate, session: Session = Depends(get_session)) -> Event:
    event = session.get(Event, id)
    if event:
        event_data = update_event.model_dump(exclude_unset=True)
        for key, value in event_data.items():
            setattr(event, key, value)
        session.add(event)
        session.commit()
        session.refresh(event)

        return event
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event not found",
    )

def raise_exception(empty_val, message: str):
    if empty_val == '':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )



def get_kr_date():
    # KST 타임존을 설정
    kst = pytz.timezone('Asia/Seoul')

    # 현재 KST 날짜와 시간 가져오기
    return datetime.now(kst).strftime('%Y-%m-%d')

