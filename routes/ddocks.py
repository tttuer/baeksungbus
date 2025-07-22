import base64

from fastapi import APIRouter, UploadFile, File, Form, Response
from fastapi.responses import RedirectResponse

from auth.authenticate import authenticate, check_admin
from models.ddock import Ddock, DdockPublic, OrderUpdateRequest

ddock_router = APIRouter(
    tags=["Ddock"],
)

# qa의 전체 리스트 반환
from fastapi import Depends
from sqlmodel import Session, select, desc, asc
from database.connection import get_session




from fastapi import Query

@ddock_router.get("", response_model=dict)
async def get_ddocks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    session: Session = Depends(get_session)
):
    offset = (page - 1) * page_size
    
    # 전체 개수 계산
    from sqlmodel import func
    total_count = session.exec(select(func.count()).select_from(Ddock)).one()
    total_pages = (total_count + page_size - 1) // page_size
    
    # 페이지네이션 적용
    statement = (
        select(Ddock)
        .order_by(asc(Ddock.order))
        .offset(offset)
        .limit(page_size)
    )
    result = session.exec(statement).all()
    
    ddocks = [
        {
            "num": offset + index,
            "id": row.id,
            "image": base64.b64encode(row.image).decode("utf-8") if row.image else None,
            "image_name": row.image_name,
            "order": row.order,
        }
        for index, row in enumerate(result)
    ]
    
    return {
        "ddocks": ddocks,
        "page": page,
        "total_pages": total_pages,
        "total_count": total_count,
    }


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
        order=ddock.order,
    )


# qa 생성
from fastapi import HTTPException, status


@ddock_router.post("", response_class=Response)
async def create_ddock(
        images: list[UploadFile] = File(...),
        user: str = Depends(authenticate),
        session: Session = Depends(get_session)) -> Response:
    check_admin(user)

    # Ddock 테이블에서 가장 최근 order 값을 가져오는 로직
    statement = (
        select(Ddock)
        .order_by(desc(Ddock.order))  # order 컬럼을 기준으로 내림차순 정렬
        .limit(1)  # 상위 1개의 레코드만 가져옴
    )

    # 실행 후 결과가 있는지 확인
    result = session.exec(statement).first()  # first()를 사용하면 결과가 없을 때 None 반환
    if result:
        last_order = result.order  # 기존 order 값 사용
    else:
        last_order = 0  # Ddock 테이블이 비어있으면 기본 값 0 설정

    # 이미지 처리 로직
    for image in images:
        content = await image.read()
        image_filename = image.filename

        last_order += 1
        ddock = Ddock(image=content, image_name=image_filename, order=last_order)

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
        deleted_order = ddock.order
        
        # 삭제할 ddock 제거
        session.delete(ddock)
        session.commit()
        
        # 삭제된 order보다 큰 order를 가진 ddock들을 1씩 감소
        statement = select(Ddock).where(Ddock.order > deleted_order).order_by(asc(Ddock.order))
        remaining_ddocks = session.exec(statement).all()
        
        for remaining_ddock in remaining_ddocks:
            remaining_ddock.order -= 1
            session.add(remaining_ddock)
        
        session.commit()
        return JSONResponse(content={"message": "삭제가 완료되었습니다."}, status_code=200)

    # QA가 존재하지 않는 경우, 404 응답 반환
    return JSONResponse(content={"message": "Ddock not found"}, status_code=404)


# 여러 개의 ddock 일괄 삭제
from pydantic import BaseModel

class BulkDeleteRequest(BaseModel):
    ids: list[int]

@ddock_router.delete("/bulk")
async def delete_ddocks_bulk(
    request: BulkDeleteRequest,
    user: str = Depends(authenticate),
    session: Session = Depends(get_session)
):
    check_admin(user)
    
    if not request.ids:
        return JSONResponse(content={"message": "삭제할 ID가 없습니다."}, status_code=400)
    
    # 삭제할 ddock들을 가져오기
    statement = select(Ddock).where(Ddock.id.in_(request.ids))
    ddocks_to_delete = session.exec(statement).all()
    
    if not ddocks_to_delete:
        return JSONResponse(content={"message": "삭제할 Ddock을 찾을 수 없습니다."}, status_code=404)
    
    # 삭제할 order들을 수집
    deleted_orders = [ddock.order for ddock in ddocks_to_delete]
    min_deleted_order = min(deleted_orders)
    
    # 삭제 실행
    for ddock in ddocks_to_delete:
        session.delete(ddock)
    session.commit()
    
    # 삭제된 order들보다 큰 order를 가진 ddock들의 order 재정렬
    statement = select(Ddock).where(Ddock.order > min_deleted_order).order_by(asc(Ddock.order))
    remaining_ddocks = session.exec(statement).all()
    
    # 삭제된 개수만큼 order 감소
    deleted_count = len(deleted_orders)
    for remaining_ddock in remaining_ddocks:
        # 현재 ddock의 order보다 작은 삭제된 order의 개수를 계산
        smaller_deleted_count = sum(1 for order in deleted_orders if order < remaining_ddock.order)
        remaining_ddock.order -= smaller_deleted_count
        session.add(remaining_ddock)
    
    session.commit()
    
    return JSONResponse(
        content={"message": f"{len(ddocks_to_delete)}개의 항목이 삭제되었습니다."},
        status_code=200
    )


@ddock_router.put("/{id}")
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



@ddock_router.patch("/order")
async def update_order(
        request: OrderUpdateRequest,
        user: str = Depends(authenticate),
        session: Session = Depends(get_session),
):
    check_admin(user)

    statement = (
        select(Ddock)
        .order_by(asc(Ddock.order))
    )
    all_ddocks = session.exec(statement).all()

    # 순서 업데이트
    for order_update in request.orders:
        for ddock in all_ddocks:
            if ddock.id == order_update.id:
                ddock.order = order_update.order
                session.add(ddock)  # 업데이트된 객체 추가

    # 데이터베이스에 변경 사항 저장
    session.commit()
    return Response(status_code=status.HTTP_200_OK)


def raise_exception(empty_val, message: str):
    if empty_val == '':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
