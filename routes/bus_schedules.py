import base64
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Response
from pydantic import BaseModel
from fastapi import HTTPException, status
from fastapi import Depends, Query
from sqlmodel import Session, select, func
from database.connection import get_session
from fastapi.responses import JSONResponse


from auth.authenticate import authenticate, check_admin
from models.bus_schedule import BusSchedule, BusSchedulePublic

schedule_router = APIRouter(
    tags=["BusSchedule"],
)

# qa의 전체 리스트 반환



@schedule_router.get("", response_model=dict)
async def get_schedules(
    filter: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    offset = (page - 1) * page_size

    # 전체 항목 수와 총 페이지 계산
    total_count = session.exec(select(func.count()).select_from(BusSchedule)).one()
    total_pages = (total_count + page_size - 1) // page_size

    if filter and filter != "":
        statement = select(BusSchedule).where(BusSchedule.route_number == filter).offset(offset).limit(page_size)
    else:
        statement = select(BusSchedule).offset(offset).limit(page_size)
    result = session.exec(statement).all()

    schedules = [
        {
            "id": row.id,
            "route_number": row.route_number,
            "url": row.url,
            "image_data": base64.b64encode(row.image_data).decode('utf-8') if row.image_data else None,
            "image_filename": row.image_filename,
        }
        for row in result
    ]

    return {
        "schedules": schedules,
        "page": page,
        "total_pages": total_pages,
        "total_count": total_count,
    }


# qa 상세보기 클릭했을때 조회
@schedule_router.get("/{id}", response_model=BusSchedulePublic)
async def get_schedule(id: int, session: Session = Depends(get_session)):
    schedule = session.get(BusSchedule, id)

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # BusSchedulePublic 모델로 반환
    return BusSchedulePublic(
        id=schedule.id,
        route_number=schedule.route_number,
        url=schedule.url,
        image_data=base64.b64encode(schedule.image_data).decode('utf-8') if schedule.image_data else None,
        image_filename=schedule.image_filename,
    )


# qa 생성


class SchduleCreateForm(BaseModel):
    route_number: str
    url: str
    image_data: Optional[str] = None  # Base64 encoded image
    image_filename: Optional[str] = None


@schedule_router.post("", response_class=Response)
async def create_schedules(
    schedules: list[SchduleCreateForm],
    user: str = Depends(authenticate),
    session: Session = Depends(get_session),
) -> Response:
    check_admin(user)

    if not schedules or len(schedules) == 0:
        return Response(status_code=400)

    # Create the schedule objects
    new_schedules = []
    for schedule in schedules:
        # Decode base64 image data if provided
        image_data = None
        if schedule.image_data:
            import base64
            image_data = base64.b64decode(schedule.image_data)

        new_schedule = BusSchedule(
            route_number=schedule.route_number,
            url=schedule.url,
            image_data=image_data,
            image_filename=schedule.image_filename,
        )
        new_schedules.append(new_schedule)

    # Add the objects to the session and save to the database
    session.add_all(new_schedules)
    session.commit()

    return Response(status_code=200)


# qa 삭제


@schedule_router.delete("/{id}")
async def delete_schedule(
    id: int, user: str = Depends(authenticate), session: Session = Depends(get_session)
):
    check_admin(user)

    schedule = session.get(BusSchedule, id)

    if schedule:
        session.delete(schedule)
        session.commit()
        return JSONResponse(
            content={"message": "삭제가 완료되었습니다."}, status_code=200
        )

    # QA가 존재하지 않는 경우, 404 응답 반환
    return JSONResponse(content={"message": "Schedule not found"}, status_code=404)


class ScheduleUpdateForm(BaseModel):
    url: str


@schedule_router.put("/{id}")
async def update_schedule(
    id: int,
    url: str = Form(None),
    image: UploadFile = File(None),
    user: str = Depends(authenticate),
    session: Session = Depends(get_session),
):
    check_admin(user)

    schedule = session.get(BusSchedule, id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    # Update URL if provided
    if url:
        schedule.url = url

    # Update image if provided
    if image:
        schedule.image_data = await image.read()
        schedule.image_filename = image.filename

    # 변경 사항 저장
    session.add(schedule)
    session.commit()

    return Response(status_code=200)


def raise_exception(empty_val, message: str):
    if empty_val == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
