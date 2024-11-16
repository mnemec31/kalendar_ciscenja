from pydantic import BaseModel
from sqlmodel import Relationship, SQLModel, Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.calendars import Calendar


class UserBase(SQLModel):
    username: str = Field(primary_key=True)


class User(UserBase, table=True):
    hashed_password: str
    calendars: list["Calendar"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
