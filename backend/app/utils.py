import icalendar
from fastapi import HTTPException, status

from app.models.calendars import Calendar, Event


def check_events_valid(events: list[Event]) -> bool:
    events.sort(key=lambda event: event.date_start)

    for event in events:
        if event.date_start >= event.date_end:
            return False

    for event, next_event in zip(events, events[1:]):
        if event.date_start == next_event.date_start:
            return False
        if event.date_end == next_event.date_end:
            return False
        if event.date_end > next_event.date_start:
            return False

    return True


def parse_calendar(file: bytes) -> Calendar:
    try:
        ical = icalendar.Calendar.from_ical(file.decode("utf-8"))
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

    if not check_events_valid(events):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Events not valid",
        )

    return calendar
