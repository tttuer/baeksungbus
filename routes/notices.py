from datetime import datetime
from typing import List

import pytz
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi import Query
from sqlalchemy.orm import selectinload
from sqlmodel import select, Session

from auth.authenticate import authenticate
from database.connection import get_session
from models.notice import Notice, NoticeShort, NoticeType, NoticeWithAnswer, NoticeUpdate

notice_router = APIRouter(
    tags=["Notice"],
)

# qa의 전체 리스트 반환
@notice_router.get("/", response_model=List[NoticeShort])
async def get_notices(
        notice_type: NoticeType,
        page: int = Query(1, ge=1),  # 기본 페이지 번호는 1
        page_size: int = Query(20, ge=1, le=100),  # 페이지 크기는 1~100 사이, 기본 20
        session: Session = Depends(get_session)
) -> List[NoticeShort]:
    offset = (page - 1) * page_size  # 페이지 번호에 따른 오프셋 계산

    # 필요한 필드만 선택해서 가져오는 쿼리 작성
    statement = (
        select(
            Notice.id,
            Notice.title,
            Notice.writer,
            Notice.c_date,
            Notice.done,
            Notice.read_cnt)
                 .where(Notice.notice_type == notice_type)
                 .offset(offset)
                 .limit(page_size))

    # 실행하고 결과를 가져옴
    result = session.exec(statement).all()

    # 필요한 필드를 CustomerQAShort로 변환
    notices_short = [
        NoticeShort(
            id=row.id,
            title=row.title,
            writer=row.writer,
            c_date=row.c_date.strftime('%Y-%m-%d'),
            done=row.done,
            read_cnt=row.read_cnt
        ) for row in result
    ]

    return notices_short


# qa 상세보기 클릭했을때 조회
@notice_router.get("/{id}", response_model=NoticeWithAnswer, response_model_exclude={"password"})
async def get_notice(id: int, password: str, session: Session = Depends(get_session)) -> NoticeWithAnswer:
    # CustomerQA를 id로 조회하고 관련된 answers를 미리 로드
    statement = select(Notice).options(selectinload(Notice.answers)).where(Notice.id == id)
    notice = session.exec(statement).first()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found",
        )
    if notice.password != password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is not correct",
        )

    return notice


# qa 생성
@notice_router.post("/", response_model=Notice)
async def create_notice(new_notice: Notice, user: str = Depends(authenticate), session=Depends(get_session)) -> Notice:
    check_admin(user)

    raise_exception(new_notice.writer, "Writer cannot be blank")
    raise_exception(new_notice.title, "Title cannot be blank")

    new_notice.c_date = get_kr_date()
    new_notice.creator = user

    session.add(new_notice)
    session.commit()
    session.refresh(new_notice)

    return new_notice

# qa 삭제
@notice_router.delete("/{id}")
async def delete_notice(id: int, user: str = Depends(authenticate), session: Session = Depends(get_session)) -> dict:
    check_admin(user)

    notice = session.get(Notice, id)

    if notice:
        session.delete(notice)
        session.commit()
        return {
            'message': 'Notice deleted',
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Customer QA not found",
    )


@notice_router.patch("/{id}")
async def update_notice(id: int, update_notice: NoticeUpdate, user: str = Depends(authenticate), session: Session = Depends(get_session)) -> Notice:
    check_admin(user)

    notice = session.get(Notice, id)
    if notice:
        notice_data = update_notice.model_dump(exclude_unset=True)
        for key, value in notice_data.items():
            setattr(notice, key, value)
        session.add(notice)
        session.commit()
        session.refresh(notice)

        return notice

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

def check_admin(user: str):
    if user != 'bsbus':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

def get_kr_date():
    # KST 타임존을 설정
    kst = pytz.timezone('Asia/Seoul')

    # 현재 KST 날짜와 시간 가져오기
    return datetime.now(kst).strftime('%Y-%m-%d')

