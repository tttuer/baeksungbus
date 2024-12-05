import base64

from fastapi import APIRouter, UploadFile, File, Form, Response
from fastapi.responses import RedirectResponse

from auth.authenticate import authenticate, check_admin
from models.bus_schedule import BusSchedule, BusSchedulePublic
from models.ddock import Ddock

ddock_router = APIRouter(
    tags=["Ddock"],
)

# qa의 전체 리스트 반환
from fastapi import Depends
from sqlmodel import Session, select
from database.connection import get_session


@ddock_router.get("", response_model=dict)
async def get_ddocks(
        session: Session = Depends(get_session)
):
    statement = (
        select(Ddock)
    )
    result = session.exec(statement).all()

    ddocks = [
        {
            "id": row.id,
            "image": base64.b64encode(row.image).decode("cp949") if row.image else None

        }
        for index, row in enumerate(result)
    ]

    return {
        "ddocks": ddocks,
    }


# qa 상세보기 클릭했을때 조회
@ddock_router.get("/{id}", response_model=BusSchedulePublic)
async def get_schedule(id: int, session: Session = Depends(get_session)):
    schedule = session.get(BusSchedule, id)

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # QAPublic 또는 QAWithAnswer 모델로 반환
    return BusSchedulePublic(
        id=schedule.id,
        image_name1=schedule.image_name1,
        image_name2=schedule.image_name2,
        image_name3=schedule.image_name3,
        image_data1=base64.b64encode(schedule.image_data1).decode("cp949") if schedule.image_data1 else None,
        image_data2=base64.b64encode(schedule.image_data2).decode("cp949") if schedule.image_data2 else None,
        image_data3=base64.b64encode(schedule.image_data3).decode("cp949") if schedule.image_data3 else None,
        title=schedule.title
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
        print(f"Received image: {image.filename}, size: {len(content)} bytes")

        ddock = Ddock(image=content)
        session.add(ddock)

    session.commit()
    return Response(status_code=status.HTTP_201_CREATED)


# qa 삭제
from fastapi.responses import JSONResponse


@ddock_router.delete("/{id}")
async def delete_schedule(id: int,
                          user: str = Depends(authenticate),
                          session: Session = Depends(get_session)):
    check_admin(user)

    schedule = session.get(BusSchedule, id)

    if schedule:
        session.delete(schedule)
        session.commit()
        return JSONResponse(content={"message": "삭제가 완료되었습니다."}, status_code=200)

    # QA가 존재하지 않는 경우, 404 응답 반환
    return JSONResponse(content={"message": "Schedule not found"}, status_code=404)


@ddock_router.put("/{id}", response_class=RedirectResponse)
async def update_schedule(
        id: int,
        title: str = Form(...),
        image_name1: str = Form(None),
        image_name2: str = Form(None),
        image_name3: str = Form(None),
        image1: UploadFile = File(None),
        image2: UploadFile = File(None),
        image3: UploadFile = File(None),
        user: str = Depends(authenticate),
        session: Session = Depends(get_session),
):
    check_admin(user)

    schedule = session.get(BusSchedule, id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer QA not found",
        )

    if not image_name1:
        schedule.image_name1 = None
        schedule.image_data1 = None
    if not image_name2:
        schedule.image_name2 = None
        schedule.image_data2 = None
    if not image_name3:
        schedule.image_name3 = None
        schedule.image_data3 = None

    if image1:
        if not image1.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미지 파일만 업로드할 수 있습니다."
            )
        schedule.image_data1 = await image1.read()
        schedule.image_name1 = image1.filename
    if image2:
        if not image1.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미지 파일만 업로드할 수 있습니다."
            )
        schedule.image_data2 = await image2.read()
        schedule.image_name2 = image2.filename
    if image3:
        if not image1.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미지 파일만 업로드할 수 있습니다."
            )
        schedule.image_data3 = await image3.read()
        schedule.image_name3 = image3.filename

    schedule.title = title

    # 변경 사항 저장
    session.add(schedule)
    session.commit()

    # 리다이렉션 수행
    return RedirectResponse(url='/adm/schedule', status_code=303)


def raise_exception(empty_val, message: str):
    if empty_val == '':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
