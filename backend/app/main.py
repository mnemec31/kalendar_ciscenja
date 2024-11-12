from typing import Annotated
from io import BytesIO

from fastapi import FastAPI, Depends, File, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
import icalendar

from app.models import Calendar, CalendarPublic, Event
from app.database import create_db_and_tables, get_session


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
    try:
        ical = icalendar.Calendar.from_ical(file)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File is malformed: {e}",
        )

    name = str(ical["PRODID"]).strip()
    content = file
    calendar = Calendar(name=name, content=content)

    try:
        events = [
            Event(
                summary=str(event["SUMMARY"]).strip(),
                date_start=event["DTSTART"].dt,
                date_end=event["DTEND"].dt,
                uid=str(event["UID"]).strip(),
                calendar=calendar,
            )
            for event in ical.walk("VEVENT")
        ]
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Event must have: summary, start, end, uid",
        )

    session.add(calendar)
    session.commit()

    return calendar


@app.get("/calendars/{calendar_id}/")
def download_calendar(session: SessionDep, calendar_id: int):
    calendar = session.exec(select(Calendar).where(Calendar.id == calendar_id)).first()
    if calendar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No calendar with that id"
        )

    if not calendar.content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calendar has no content"
        )

    file_stream = BytesIO(calendar.content)

    response = StreamingResponse(file_stream, media_type="text/calendar")
    response.headers["Content-Disposition"] = (
        f"attachment; filename=calendar_{calendar_id}.ics"
    )
    return response
