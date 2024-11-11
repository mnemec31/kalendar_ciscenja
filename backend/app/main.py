from typing import Annotated
from fastapi import FastAPI, Depends, File, Query
from sqlmodel import Session, select
import icalendar

from app.models import Calendar, CalendarPublic, Event
from app.database import create_db_and_tables, engine, get_session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


create_db_and_tables()


@app.get("/calendars/", response_model=list[CalendarPublic])
async def get_calendars(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    calendars = session.exec(select(Calendar).offset(offset).limit(limit)).all()
    return calendars


@app.post("/import-calendar/", response_model=CalendarPublic)
async def upload_calendar(session: SessionDep, file: Annotated[bytes, File()]):
    ical = icalendar.Calendar.from_ical(file)

    name = str(ical["PRODID"]).strip()
    calendar = Calendar(name=name)

    events = []

    for event in ical.walk("VEVENT"):
        events.append(
            Event(
                summary=str(event["SUMMARY"]).strip(),
                date_start=event["DTSTART"].dt,
                date_end=event["DTEND"].dt,
                uid=str(event["UID"]).strip(),
                calendar=calendar,
            )
        )

    session.add(calendar)
    session.commit()

    return calendar
