import datetime
from pydantic import BaseModel
from sqlmodel import Relationship, SQLModel, Field


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


class CalendarBase(SQLModel):
    name: str | None = Field(default=None)
    id: int | None = Field(default=None, primary_key=True)
    url: str | None = Field(default=None)


class Calendar(CalendarBase, table=True):
    user_id: str | None = Field(default=None, foreign_key="user.username")
    user: User = Relationship(back_populates="calendars")
    events: list["Event"] = Relationship(back_populates="calendar")
    content: bytes | None


class CalendarUrlImport(SQLModel):
    url: str


class EventBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    uid: str | None = Field(default=None)
    summary: str | None = Field(default=None)
    date_start: datetime.date | None = Field(default=None)
    date_end: datetime.date | None = Field(default=None)


class Event(EventBase, table=True):
    calendar_id: int | None = Field(default=None, foreign_key="calendar.id")
    calendar: Calendar = Relationship(back_populates="events")


class EventPublic(EventBase):
    pass


class CalendarPublic(CalendarBase):
    events: list[EventPublic] | None = None
