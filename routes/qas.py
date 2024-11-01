from datetime import datetime

import pytz
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import selectinload

from models.qa import QAWithAnswer, QAUpdate, QARetrieve

qa_router = APIRouter(
    tags=["Qa"],
)

# qa의 전체 리스트 반환
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from models.qa import QA, QAType
from database.connection import get_session

qa_router = APIRouter()


@qa_router.get("/", response_model=dict)
async def get_qas(
        qa_type: QAType,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        session: Session = Depends(get_session)
):
    offset = (page - 1) * page_size

    # 전체 항목 수와 총 페이지 계산
    total_count = session.exec(select(func.count()).select_from(QA).where(QA.qa_type == qa_type)).one()
    total_pages = (total_count + page_size - 1) // page_size

    # 필요한 필드만 선택해서 가져오는 쿼리 작성

    statement = (
        select(QA)
        .where(QA.qa_type == qa_type)
        .offset(offset)
        .limit(page_size)
    )
    result = session.exec(statement).all()

    # 필요한 필드를 CustomerQAShort로 변환
    qas_short = [
        {
            "id": row.id,
            "num": index + 1,
            "title": row.title,
            "writer": row.writer,
            "c_date": row.c_date,
            "done": row.done,
            "hidden": row.hidden,
            "read_cnt": row.read_cnt,
            "attachment_filename": row.attachment_filename,
        }
        for index, row in enumerate(result)

    ]

    qas_short.reverse()

    return {
        "qas": qas_short,
        "page": page,
        "total_pages": total_pages
    }


# qa 상세보기 클릭했을때 조회
@qa_router.get("/{id}", response_model=QAWithAnswer, response_model_exclude={"password", "answers.customer_qa_id"})
async def get_qa(id: int, session: Session = Depends(get_session)) -> QAWithAnswer:
    # CustomerQA를 id로 조회하고 관련된 answers를 미리 로드
    statement = select(QA).options(selectinload(QA.answers)).where(QA.id == id)
    qa = session.exec(statement).first()

    if not qa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CustomerQA not found",
        )
    return qa


# qa 생성
@qa_router.post("/", response_class=RedirectResponse)
async def create_qa(
        writer: str = Form(...),
        email: str = Form(None),
        password: str = Form(...),
        title: str = Form(...),
        content: str = Form(None),
        hidden: bool = Form(False),
        qa_type: QAType = Form(QAType.CUSTOMER),
        attachment: UploadFile = File(None),
        redirect_url: str = Form(None),
        session: Session = Depends(get_session)) -> QARetrieve:
    # Read file content and get file name
    attachment_data = await attachment.read() if attachment else None
    attachment_filename = attachment.filename if attachment else None

    # Create the QA object
    new_qa = QA(
        writer=writer,
        email=email,
        password=password,
        title=title,
        content=content,
        attachment=attachment_data,  # Store the file data as bytes
        hidden=hidden,
        qa_type=qa_type,
        c_date=get_kr_date().format('%Y-%m-%d'),
        attachment_filename=attachment_filename,
    )

    # Add the object to the session and save to the database
    session.add(new_qa)
    session.commit()
    session.refresh(new_qa)

    return RedirectResponse(url=redirect_url, status_code=303)


# qa 삭제
@qa_router.delete("/{id}")
async def delete_qa(id: int, password: str, session: Session = Depends(get_session)) -> dict:
    qa = session.get(QA, id)
    if qa:
        if password == qa.password:
            session.delete(qa)
            session.commit()
            return {
                'message': 'Customer QA deleted',
            }
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect",
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Customer QA not found",
    )


@qa_router.patch("/{id}")
async def update_qa(id: int, password: str, update_qa: QAUpdate, session: Session = Depends(get_session)) -> QA:
    qa = session.get(QA, id)
    if qa:
        if qa.password == password:
            event_data = update_qa.model_dump(exclude_unset=True)
            for key, value in event_data.items():
                setattr(qa, key, value)
            session.add(qa)
            session.commit()
            session.refresh(qa)

            return qa

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password incorrect",
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Customer QA not found",
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
