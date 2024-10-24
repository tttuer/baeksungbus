from sqlmodel import SQLModel, Field, JSON, Column, Relationship

class AnswerBase(SQLModel):
    content: str
    qa_id: int = Field(default=None, foreign_key="qa.id", ondelete='CASCADE')


class Answer(AnswerBase, table=True):
    __tablename__ = 'answer'
    id: int = Field(primary_key=True, default=None)

    # CustomerQA와의 관계
    qa: "QA" = Relationship(back_populates="answers")
    class Config:
        json_schema_extra = {
            'example': {
                'content': 'example content',
            }
        }


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
