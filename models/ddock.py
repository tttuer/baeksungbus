from typing import Optional

from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class DdockBase(SQLModel):
    image: Optional[bytes] = None
    image_name: Optional[str] = None
    order: int = None


class Ddock(DdockBase, table=True):
    __tablename__ = 'ddock'
    id: int = Field(primary_key=True, default=None)


class QAShort(SQLModel):
    id: int


class DdockPublic(BaseModel):
    id: int
    image: Optional[str] = None
    image_name: Optional[str] = None
    order: int = None


class DdockOrder(BaseModel):
    id: int
    order: int


class OrderUpdateRequest(BaseModel):
    orders: list[DdockOrder]
