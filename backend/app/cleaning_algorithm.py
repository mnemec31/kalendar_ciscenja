from datetime import date
from dataclasses import dataclass
from .models import Calendar, CleaningDate


@dataclass
class Event:
    date_start: date
    date_end: date

    def __lt__(self, other):
        return self.date_start < other.date_start


@dataclass
class CleaningBuffer:
    calendar_id: int
    start: date
    end: date
    cleaned: bool = False

    def __lt__(self, other):
        """
        For cleaning buffer we want to now which one "expires" first (has the oldest end date)
        """
        return self.end < other.end

    def can_be_cleaned_with_other(self, other):
        return not (self.start > other.end or self.end < other.start)


def create_cleaning_buffers(calendars: list[Calendar]) -> list[CleaningBuffer]:
    cleaning_buffers: list[CleaningBuffer] = []

    for calendar in calendars:
        events = [
            Event(
                date_start=event.date_start,
                date_end=event.date_end,
            )
            for event in calendar.events
        ]
        # Sort events by starting dates
        events.sort()

        # We know that:
        #   1. events are sorted
        #   2. events don't have overlap (because we don't allow them when creating calendars)
        # Cleaning buffer can then be found by looking at the difference between end of current
        # event and start of the next event
        for event, next_event in zip(events, events[1:]):
            cleaning_buffers.append(
                CleaningBuffer(
                    calendar_id=calendar.id,
                    start=event.date_end,
                    end=next_event.date_start,
                )
            )

    return cleaning_buffers


def calculate_cleaning_times(calendars: list[Calendar]) -> list[CleaningDate]:
    """
    Algorithm:
        - find all intervals which are free for cleaning (i.e. not occupied by guests) and save them to a list
        - pick first cleaning interval that "expires"
        - check which other apartments can be cleaned in that same interval
        - repeat until all cleaning intervals are cleaned
    """

    cleaning_times: list[CleaningDate] = []

    cleaning_buffers = create_cleaning_buffers(calendars)

    while True:
        not_cleaned_buffers = [
            buffer for buffer in cleaning_buffers if not buffer.cleaned
        ]

        if not not_cleaned_buffers:
            break

        first_expiring = min(not_cleaned_buffers)

        for buffer in not_cleaned_buffers:
            if buffer.can_be_cleaned_with_other(first_expiring):
                buffer.cleaned = True
                cleaning_times.append(
                    CleaningDate(
                        calendar_id=buffer.calendar_id,
                        date=first_expiring.end,
                    )
                )

    return cleaning_times
