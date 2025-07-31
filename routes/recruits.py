from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from typing import List

from auth.authenticate import authenticate
from database.connection import get_session
from models.recruit import Recruit, RecruitExperience, RecruitPublic, RecruitRequest

recruit_router = APIRouter(
    tags=["Recruit"],
)


@recruit_router.get("", response_model=List[RecruitPublic])
async def get_recruits(session: Session = Depends(get_session)) -> List[RecruitPublic]:
    """표시 설정된 채용 정보를 가져옵니다."""
    recruits = session.exec(select(Recruit).where(Recruit.show == True)).all()

    result = []
    for recruit in recruits:
        # 각 채용에 대한 경력 요구사항 조회
        experiences = session.exec(
            select(RecruitExperience).where(RecruitExperience.recruit_id == recruit.id)
        ).all()

        recruit_public = RecruitPublic(
            id=recruit.id,
            title=recruit.title,
            department=recruit.department,
            experience=[
                {"label": exp.label, "value": exp.value} for exp in experiences
            ],
            note=recruit.note,
            show=recruit.show,
        )
        result.append(recruit_public)

    return result


@recruit_router.get("/admin/all", response_model=List[RecruitPublic])
async def get_all_recruits_admin(
    user: str = Depends(authenticate), session: Session = Depends(get_session)
) -> List[RecruitPublic]:
    """관리자용: show 상태와 관계없이 모든 채용 정보를 가져옵니다."""
    check_admin(user)
    
    recruits = session.exec(select(Recruit)).all()

    result = []
    for recruit in recruits:
        # 각 채용에 대한 경력 요구사항 조회
        experiences = session.exec(
            select(RecruitExperience).where(RecruitExperience.recruit_id == recruit.id)
        ).all()

        recruit_public = RecruitPublic(
            id=recruit.id,
            title=recruit.title,
            department=recruit.department,
            experience=[
                {"label": exp.label, "value": exp.value} for exp in experiences
            ],
            note=recruit.note,
            show=recruit.show,
        )
        result.append(recruit_public)

    return result


@recruit_router.get("/{id}", response_model=RecruitPublic)
async def get_recruit(
    id: int, session: Session = Depends(get_session)
) -> RecruitPublic:
    """특정 채용 정보를 가져옵니다."""
    recruit = session.get(Recruit, id)

    if not recruit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruit not found",
        )

    # 경력 요구사항 조회
    experiences = session.exec(
        select(RecruitExperience).where(RecruitExperience.recruit_id == recruit.id)
    ).all()

    return RecruitPublic(
        id=recruit.id,
        title=recruit.title,
        department=recruit.department,
        experience=[{"label": exp.label, "value": exp.value} for exp in experiences],
        note=recruit.note,
        show=recruit.show,
    )


@recruit_router.post("")
async def create_recruit(
    recruit_request: RecruitRequest,
    user: str = Depends(authenticate),
    session: Session = Depends(get_session),
):
    """새로운 채용 정보를 생성합니다."""
    check_admin(user)

    if not recruit_request.title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be blank",
        )

    # 채용 정보 생성
    new_recruit = Recruit(
        title=recruit_request.title,
        department=recruit_request.department,
        note=recruit_request.note,
        show=recruit_request.show,
    )

    session.add(new_recruit)
    session.commit()
    session.refresh(new_recruit)

    # 경력 요구사항 생성
    for exp in recruit_request.experience:
        recruit_experience = RecruitExperience(
            recruit_id=new_recruit.id, label=exp.label, value=exp.value
        )
        session.add(recruit_experience)

    session.commit()

    return {"message": "Recruit created successfully", "id": new_recruit.id}


@recruit_router.patch("/{id}")
async def update_recruit(
    id: int,
    recruit_request: RecruitRequest,
    user: str = Depends(authenticate),
    session: Session = Depends(get_session),
):
    """채용 정보를 수정합니다."""
    check_admin(user)

    recruit = session.get(Recruit, id)
    if not recruit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruit not found",
        )

    # 기본 정보 업데이트
    recruit.title = recruit_request.title
    recruit.department = recruit_request.department
    recruit.note = recruit_request.note
    recruit.show = recruit_request.show

    # 기존 경력 요구사항 삭제
    existing_experiences = session.exec(
        select(RecruitExperience).where(RecruitExperience.recruit_id == id)
    ).all()

    for exp in existing_experiences:
        session.delete(exp)

    # 새로운 경력 요구사항 추가
    for exp in recruit_request.experience:
        recruit_experience = RecruitExperience(
            recruit_id=id, label=exp.label, value=exp.value
        )
        session.add(recruit_experience)

    session.commit()
    session.refresh(recruit)

    return {"message": "Recruit updated successfully"}


@recruit_router.delete("/{id}")
async def delete_recruit(
    id: int, user: str = Depends(authenticate), session: Session = Depends(get_session)
) -> dict:
    """채용 정보를 삭제합니다."""
    check_admin(user)

    recruit = session.get(Recruit, id)

    if not recruit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruit not found",
        )

    # 관련된 경력 요구사항도 함께 삭제
    experiences = session.exec(
        select(RecruitExperience).where(RecruitExperience.recruit_id == id)
    ).all()

    for exp in experiences:
        session.delete(exp)

    session.delete(recruit)
    session.commit()

    return {"message": "Recruit deleted successfully"}


def check_admin(user: str):
    """관리자 권한을 확인합니다."""
    if user != "bsbus":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
