from datetime import datetime
from sqlmodel import Relationship, SQLModel, Field


class CalendarBase(SQLModel):
    name: str | None = Field(default=None)
    id: int | None = Field(default=None, primary_key=True)


class Calendar(CalendarBase, table=True):
    events: list["Event"] = Relationship(back_populates="calendar")


class EventBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    uid: str | None = Field(default=None)
    summary: str | None = Field(default=None)
    date_start: datetime | None = Field(default=None)
    date_end: datetime | None = Field(default=None)


class Event(EventBase, table=True):
    calendar_id: int | None = Field(default=None, foreign_key="calendar.id")
    calendar: Calendar = Relationship(back_populates="events")


class EventPublic(EventBase):
    pass


class CalendarPublic(CalendarBase):
    events: list[EventPublic] | None = None
