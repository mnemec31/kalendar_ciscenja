from typing import Annotated
from fastapi import FastAPI, Depends, Query
from sqlmodel import Session, select

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
