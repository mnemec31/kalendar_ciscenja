import icalendar
from fastapi import HTTPException, status

from .models import Calendar, Event


def parse_calendar(file: bytes) -> Calendar:
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
        _ = [
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

    return calendar
