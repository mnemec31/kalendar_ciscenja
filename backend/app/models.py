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
    content: bytes | None
    events: list["Event"] = Relationship(back_populates="calendar")
    cleaning_dates: list["CleaningDate"] = Relationship(back_populates="calendar")


class CalendarUrlImport(SQLModel):
    url: str


class CleaningDateBase(SQLModel):
    date: datetime.date


class CleaningDate(CleaningDateBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    calendar_id: int | None = Field(default=None, foreign_key="calendar.id")
    calendar: Calendar = Relationship(back_populates="cleaning_dates")


class CleaningDatePublic(CleaningDateBase):
    pass


class EventBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    uid: str | None = Field(default=None)
    summary: str | None = Field(default=None)
    date_start: datetime.date = Field(default=None)
    date_end: datetime.date = Field(default=None)


class Event(EventBase, table=True):
    calendar_id: int | None = Field(default=None, foreign_key="calendar.id")
    calendar: Calendar = Relationship(back_populates="events")


class EventPublic(EventBase):
    pass


class CalendarPublic(CalendarBase):
    events: list[EventPublic] | None = None
    cleaning_dates: list[CleaningDatePublic] | None = None
