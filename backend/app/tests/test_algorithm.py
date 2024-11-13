import pytest

from app.cleaning_algorithm import calculate_cleaning_times
from app.models import Calendar, Event, CleaningDate
import datetime


def test_empty():
    calendars = []
    assert calculate_cleaning_times(calendars) == []


def test_one_calendar_one_event():
    calendars = [
        Calendar(
            id=1,
            events=[
                Event(
                    id=1,
                    date_start=datetime.date(2024, 9, 30),
                    date_end=datetime.date(2024, 10, 2),
                )
            ],
        ),
    ]
    assert calculate_cleaning_times(calendars) == []


def test_one_calendar_one_cleaning_time():
    calendars = [
        Calendar(
            id=1,
            events=[
                Event(
                    id=1,
                    date_start=datetime.date(2024, 9, 30),
                    date_end=datetime.date(2024, 10, 2),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 4),
                    date_end=datetime.date(2024, 10, 7),
                ),
            ],
        ),
    ]
    assert calculate_cleaning_times(calendars) == [
        CleaningDate(date=datetime.date(2024, 10, 4), calendar_id=1)
    ]


def test_one_calendar_multiple_cleaning_times():
    calendars = [
        Calendar(
            id=1,
            events=[
                Event(
                    id=1,
                    date_start=datetime.date(2024, 9, 30),
                    date_end=datetime.date(2024, 10, 2),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 4),
                    date_end=datetime.date(2024, 10, 7),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 15),
                    date_end=datetime.date(2024, 10, 17),
                ),
            ],
        ),
    ]
    assert calculate_cleaning_times(calendars) == [
        CleaningDate(date=datetime.date(2024, 10, 4), calendar_id=1),
        CleaningDate(date=datetime.date(2024, 10, 15), calendar_id=1),
    ]


def test_two_calendars_same_events():
    calendars = [
        Calendar(
            id=1,
            events=[
                Event(
                    id=1,
                    date_start=datetime.date(2024, 9, 30),
                    date_end=datetime.date(2024, 10, 2),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 4),
                    date_end=datetime.date(2024, 10, 7),
                ),
            ],
        ),
        Calendar(
            id=2,
            events=[
                Event(
                    id=1,
                    date_start=datetime.date(2024, 9, 30),
                    date_end=datetime.date(2024, 10, 2),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 4),
                    date_end=datetime.date(2024, 10, 7),
                ),
            ],
        ),
    ]
    assert calculate_cleaning_times(calendars) == [
        CleaningDate(date=datetime.date(2024, 10, 4), calendar_id=1),
        CleaningDate(date=datetime.date(2024, 10, 4), calendar_id=2),
    ]


def test_two_calendars_no_cleaning_intersect():
    calendars = [
        Calendar(
            id=1,
            events=[
                Event(
                    id=1,
                    date_start=datetime.date(2024, 9, 30),
                    date_end=datetime.date(2024, 10, 2),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 4),
                    date_end=datetime.date(2024, 10, 7),
                ),
            ],
        ),
        Calendar(
            id=2,
            events=[
                Event(
                    id=1,
                    date_start=datetime.date(2024, 9, 30),
                    date_end=datetime.date(2024, 10, 5),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 5),
                    date_end=datetime.date(2024, 10, 6),
                ),
            ],
        ),
    ]
    assert calculate_cleaning_times(calendars) == [
        CleaningDate(date=datetime.date(2024, 10, 4), calendar_id=1),
        CleaningDate(date=datetime.date(2024, 10, 5), calendar_id=2),
    ]


def test_two_calendars_two_events():
    calendars = [
        Calendar(
            id=1,
            events=[
                Event(
                    id=1,
                    date_start=datetime.date(2024, 9, 30),
                    date_end=datetime.date(2024, 10, 2),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 4),
                    date_end=datetime.date(2024, 10, 7),
                ),
            ],
        ),
        Calendar(
            id=2,
            events=[
                Event(
                    id=1,
                    date_start=datetime.date(2024, 9, 30),
                    date_end=datetime.date(2024, 10, 1),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 3),
                    date_end=datetime.date(2024, 10, 6),
                ),
            ],
        ),
    ]
    assert calculate_cleaning_times(calendars) == [
        CleaningDate(date=datetime.date(2024, 10, 3), calendar_id=1),
        CleaningDate(date=datetime.date(2024, 10, 3), calendar_id=2),
    ]


def test_multiple_calendars_multiple_events():
    calendars = [
        Calendar(
            id=1,
            events=[
                Event(
                    id=1,
                    date_start=datetime.date(2024, 9, 30),
                    date_end=datetime.date(2024, 10, 2),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 4),
                    date_end=datetime.date(2024, 10, 10),
                ),
            ],
        ),
        Calendar(
            id=2,
            events=[
                Event(
                    id=1,
                    date_start=datetime.date(2024, 9, 30),
                    date_end=datetime.date(2024, 10, 3),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 5),
                    date_end=datetime.date(2024, 10, 10),
                ),
            ],
        ),
        Calendar(
            id=3,
            events=[
                Event(
                    id=1,
                    date_start=datetime.date(2024, 9, 30),
                    date_end=datetime.date(2024, 10, 1),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 1),
                    date_end=datetime.date(2024, 10, 4),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 6),
                    date_end=datetime.date(2024, 10, 8),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 8),
                    date_end=datetime.date(2024, 10, 10),
                ),
            ],
        ),
        Calendar(
            id=4,
            events=[
                Event(
                    id=1,
                    date_start=datetime.date(2024, 9, 30),
                    date_end=datetime.date(2024, 10, 10),
                ),
                Event(
                    id=1,
                    date_start=datetime.date(2024, 10, 10),
                    date_end=datetime.date(2024, 10, 11),
                ),
            ],
        ),
    ]
    assert calculate_cleaning_times(calendars) == [
        CleaningDate(date=datetime.date(2024, 10, 1), calendar_id=3),
        CleaningDate(date=datetime.date(2024, 10, 4), calendar_id=1),
        CleaningDate(date=datetime.date(2024, 10, 4), calendar_id=2),
        CleaningDate(date=datetime.date(2024, 10, 4), calendar_id=3),
        CleaningDate(date=datetime.date(2024, 10, 8), calendar_id=3),
        CleaningDate(date=datetime.date(2024, 10, 10), calendar_id=4),
    ]
