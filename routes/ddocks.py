import base64
from functools import lru_cache

from fastapi import APIRouter, UploadFile, File, Form, Response
from fastapi.responses import RedirectResponse

from auth.authenticate import authenticate, check_admin
from models.ddock import Ddock, DdockPublic

ddock_router = APIRouter(
    tags=["Ddock"],
)

# qa의 전체 리스트 반환
from fastapi import Depends
from sqlmodel import Session, select
from database.connection import get_session


# 데이터베이스 쿼리 함수 캐싱
@lru_cache(maxsize=100)
def get_cached_ddocks(session: Session):
    statement = select(Ddock)
    result = session.exec(statement).all()
    return [
        {
            "num": index,
            "id": row.id,
            "image": base64.b64encode(row.image).decode("cp949") if row.image else None,
            "image_name": row.image_name,
        }
        for index, row in enumerate(result)
    ]


@ddock_router.get("", response_model=dict)
async def get_ddocks(session: Session = Depends(get_session)):
    ddocks = get_cached_ddocks(session)
    return {"ddocks": ddocks}


# qa 상세보기 클릭했을때 조회
@ddock_router.get("/{id}", response_model=DdockPublic)
async def get_ddock(id: int, user: str = Depends(authenticate), session: Session = Depends(get_session)):
    check_admin(user)

    ddock = session.get(Ddock, id)

    if not ddock:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # QAPublic 또는 QAWithAnswer 모델로 반환
    return DdockPublic(
        id=ddock.id,
        image=base64.b64encode(ddock.image).decode("cp949") if ddock.image else None,
        image_name=ddock.image_name,
    )


# qa 생성
from fastapi import HTTPException, status


@ddock_router.post("", response_class=Response)
async def create_ddock(
        images: list[UploadFile] = File(...),
        user: str = Depends(authenticate),
        session: Session = Depends(get_session)) -> Response:
    check_admin(user)

    # 이미지 처리 로직
    for image in images:
        content = await image.read()
        image_filename = image.filename
        print(f"Received image: {image.filename}, size: {len(content)} bytes")

        ddock = Ddock(image=content, image_name=image_filename)
        session.add(ddock)

    session.commit()
    return Response(status_code=status.HTTP_201_CREATED)


# qa 삭제
from fastapi.responses import JSONResponse


@ddock_router.delete("/{id}")
async def delete_ddock(id: int,
                       user: str = Depends(authenticate),
                       session: Session = Depends(get_session)):
    check_admin(user)

    ddock = session.get(Ddock, id)

    if ddock:
        session.delete(ddock)
        session.commit()
        return JSONResponse(content={"message": "삭제가 완료되었습니다."}, status_code=200)

    # QA가 존재하지 않는 경우, 404 응답 반환
    return JSONResponse(content={"message": "Ddock not found"}, status_code=404)


@ddock_router.put("/{id}", response_class=RedirectResponse)
async def update_ddock(
        id: int,
        image_name: str = Form(None),
        image: UploadFile = File(None),
        user: str = Depends(authenticate),
        session: Session = Depends(get_session),
):
    check_admin(user)

    ddock = session.get(Ddock, id)
    if not ddock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ddock not found",
        )

    if not image_name:
        ddock.image_name = None
        ddock.image = None

    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미지 파일만 업로드할 수 있습니다."
            )
        ddock.image = await image.read()
        ddock.image_name = image.filename

    # 변경 사항 저장
    session.add(ddock)
    session.commit()

    # 리다이렉션 수행
    return RedirectResponse(url='/adm/ddock', status_code=303)


def raise_exception(empty_val, message: str):
    if empty_val == '':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
