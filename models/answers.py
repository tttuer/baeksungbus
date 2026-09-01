import base64
from typing import Optional

from pydantic import field_serializer
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import LONGBLOB, LONGTEXT, VARCHAR
from sqlmodel import SQLModel, Field, Relationship


class AnswerBase(SQLModel):
    content: str = Field(sa_column=Column(LONGTEXT, nullable=False))
    qa_id: int = Field(default=None, foreign_key="qa.id", ondelete='CASCADE')
    creator: Optional[str]
    attachment: Optional[bytes] = Field(default=None, sa_column=Column(LONGBLOB))
    attachment_filename: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(1024)))


class Answer(AnswerBase, table=True):
    __tablename__ = 'answer'
    id: int = Field(primary_key=True, default=None)

    # CustomerQA와의 관계
    qa: "QA" = Relationship(back_populates="answers")

    @field_serializer("attachment")
    def serialize_attachment(self, attachment: Optional[bytes]) -> Optional[str]:
        return base64.b64encode(attachment).decode() if attachment else None

    class Config:
        json_schema_extra = {
            'example': {
                'content': 'example content',
            }
        }

class AnswerUpdate(SQLModel):
    content: str

# class UserSingIn(BaseModel):
#     email: EmailStr
#     password: str
#
#     class Config:
#         json_schema_extra = {
#             'example': {
#                 'email': 'ex.example.com',
#                 'password': '<PASSWORD>',
#             }
#         }
