from typing import Optional

from pydantic import EmailStr, BaseModel
from sqlmodel import SQLModel, Field


class BusScheduleBase(SQLModel):
    route_number: str
    url: str


class BusSchedule(BusScheduleBase, table=True):
    __tablename__ = 'bus_schedule'
    id: int = Field(primary_key=True, default=None)
    images: Optional[str] = None  # JSON string: [{"data": "base64", "filename": "name"}]


class QAShort(SQLModel):
    id: int


class BusSchedulePublic(BaseModel):
    id: int
    route_number: str
    url: str
    images: Optional[list] = None  # [{"data": "base64", "filename": "name"}]


class QAUpdate(SQLModel):
    writer: Optional[str] = None
    email: Optional[EmailStr] = None
    title: Optional[str] = None
    content: Optional[str] = None
    attachment: Optional[bytes] = None
    hidden: Optional[bool] = None


class QACreate(BaseModel):
    writer: str
    email: Optional[EmailStr] = None
    password: str
    title: str
    content: Optional[str] = None
    hidden: bool = False


class QARetrieve(BaseModel):
    id: int
    writer: str
    email: Optional[str]
    title: str
    content: Optional[str]
    c_date: Optional[str]
    done: bool
    read_cnt: int
    hidden: bool
    attachment_filename: Optional[str] = None  # Add filename field

    class Config:
        from_attributes = True
