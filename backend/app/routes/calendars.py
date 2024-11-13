from io import BytesIO
from typing import Annotated, Optional
import datetime

import requests
from pydantic import HttpUrl, ValidationError
from fastapi import APIRouter, File, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel import select

from app.crud import get_user_by_username
from app.deps import SessionDep, CurrentUser
from app.models import Calendar, CalendarPublic, CalendarUrlImport, User
from app import utils

router = APIRouter()


@router.get("/calendars/", response_model=list[CalendarPublic])
async def get_calendars(
    session: SessionDep,
    current_user: CurrentUser,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    from_date: Optional[datetime.date] = Query(default=None),
    to_date: Optional[datetime.date] = Query(default=None),
):
    user = session.exec(
        select(User)
        .where(User.username == current_user.username)
        .offset(offset)
        .limit(limit)
    ).first()

    if not (from_date or to_date):
        return user.calendars

    calendar_list = []
    for calendar in user.calendars:
        filtered_events = [
            event
            for event in calendar.events
            if (not from_date or event.date_end >= from_date)
            and (not to_date or event.date_start <= to_date)
        ]
        calendar_public = CalendarPublic(
            **calendar.model_dump(), events=filtered_events
        )

        calendar_list.append(calendar_public)

    return calendar_list


@router.get("/calendars/{calendar_id}/")
def download_calendar(session: SessionDep, current_user: CurrentUser, calendar_id: int):
    calendar = session.exec(select(Calendar).where(Calendar.id == calendar_id)).first()
    if calendar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No calendar with that id"
        )

    if calendar.user != get_user_by_username(session, current_user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Calendar doesn't belong to that user",
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


@router.post("/import-calendar/", response_model=CalendarPublic)
async def upload_calendar(
    session: SessionDep, current_user: CurrentUser, file: Annotated[bytes, File()]
):
    calendar = utils.parse_calendar(file)

    user = get_user_by_username(session, current_user.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No user with that username"
        )

    calendar.user = get_user_by_username(session, current_user.username)

    session.add(calendar)
    session.commit()

    return calendar


@router.post("/import-from-url/", response_model=CalendarPublic)
async def import_calendar_from_url(
    session: SessionDep, current_user: CurrentUser, calendar_url: CalendarUrlImport
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

    calendar = utils.parse_calendar(rsp)
    calendar.user = get_user_by_username(session, current_user.username)
    calendar.url = calendar_url.url

    session.add(calendar)
    session.commit()

    return calendar
