from typing import Annotated
from io import BytesIO
import requests

from fastapi import FastAPI, Depends, File, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import HttpUrl, ValidationError
from sqlmodel import Session, select

from app.models import Calendar, CalendarPublic, CalendarUrlImport, Event
from app.database import create_db_and_tables, get_session
from app.utils import parse_calendar

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


@app.post("/import-calendar/", response_model=CalendarPublic)
async def upload_calendar(session: SessionDep, file: Annotated[bytes, File()]):
    calendar = parse_calendar(file)

    session.add(calendar)
    session.commit()

    return calendar


@app.post("/import-from-url/", response_model=CalendarPublic)
async def import_calendar_from_url(
    session: SessionDep, calendar_url: CalendarUrlImport
):
    try:
        HttpUrl(calendar_url.url)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid URL: {e}"
        )

    try:
        rsp = requests.get(calendar_url.url).content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot get file from {calendar_url.url}: {e}",
        )

    calendar = parse_calendar(rsp)
    calendar.url = calendar_url.url

    session.add(calendar)
    session.commit()

    return calendar
