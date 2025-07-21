from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class Experience(BaseModel):
    label: str
    value: str


class RecruitBase(SQLModel):
    title: str
    department: str
    note: Optional[str] = None


class Recruit(RecruitBase, table=True):
    __tablename__ = 'recruit'
    id: int = Field(primary_key=True, default=None)
    
    class Config:
        json_schema_extra = {
            'example': {
                'title': '승무직',
                'department': '승무사원',
                'note': '※ 여객자동차운수사업법에 따라 운수종사자로서 결격사유가 없어야 함'
            }
        }


class RecruitExperience(SQLModel, table=True):
    __tablename__ = 'recruit_experience'
    id: int = Field(primary_key=True, default=None)
    recruit_id: int = Field(foreign_key="recruit.id")
    label: str
    value: str


class RecruitPublic(BaseModel):
    id: int
    title: str
    department: str
    experience: List[Experience]
    note: Optional[str] = None


class RecruitRequest(SQLModel):
    title: str
    department: str
    experience: List[Experience]
    note: Optional[str] = None