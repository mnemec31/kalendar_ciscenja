import pytest
import hashlib

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app, get_session
from app.models import Calendar, Event


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


TEST_FILES_PATH = "app/tests/test_files"


def test_get_calendars_empty(client: TestClient):
    response = client.get("/calendars")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == []


def test_download_calendar_nonexisting(client: TestClient):
    response = client.get("/calendars/1")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_calendars(session: Session, client: TestClient):
    calendar_name = "test calendar 1"
    calendar1 = Calendar(name=calendar_name)

    event1_summary = "Ivica"
    event1 = Event(summary=event1_summary, calendar=calendar1)
    event2_summary = "Perica"
    event2 = Event(summary=event2_summary, calendar=calendar1)

    session.add(calendar1)
    session.commit()

    response = client.get("/calendars")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data[0]["name"] == calendar_name
    assert data[0]["events"][0]["summary"] == event1_summary
    assert data[0]["events"][1]["summary"] == event2_summary


def test_upload_calendar_valid(client: TestClient):
    with open(f"{TEST_FILES_PATH}/valid/apartment_1.ics", "rb") as f:
        response = client.post(
            "/import-calendar",
            files={"file": f},
        )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["name"] == "primjer zadatka - apartment 1"
    assert data["id"] == 1
    assert data["events"] == [
        {
            "id": 1,
            "uid": "aca171cfaa8cf1c5765e64e819906485",
            "summary": "Ivica",
            "date_start": "2020-09-30T00:00:00",
            "date_end": "2020-10-02T00:00:00",
        },
        {
            "id": 2,
            "uid": "26db1820702b397cc969489412b44f6a",
            "summary": "Jurica",
            "date_start": "2020-10-04T00:00:00",
            "date_end": "2020-10-10T00:00:00",
        },
    ]


def test_upload_calendar_invalid(client: TestClient):
    INVALID_FILES_LIST = [
        "empty.ics",
        "event_no_start_and_end.ics",
        "malformed.ics",
        "no_begin.ics",
        "no_begin_event.ics",
        "no_end.ics",
        "no_prodid.ics",
        "no_summary.ics",
    ]

    for invalid_file in INVALID_FILES_LIST:
        with open(f"{TEST_FILES_PATH}/invalid/{invalid_file}", "rb") as f:
            response = client.post(
                "/import-calendar",
                files={"file": f},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_and_download(client: TestClient):
    with open(f"{TEST_FILES_PATH}/valid/apartment_1.ics", "rb") as f:
        original_file_checksum = hashlib.md5(f.read()).hexdigest()

        response = client.post(
            "/import-calendar",
            files={"file": f},
        )

    assert response.status_code == status.HTTP_200_OK

    response = client.get("/calendars/1")
    assert response.status_code == status.HTTP_200_OK

    received_file_checksum = hashlib.md5(response.read()).hexdigest()
    assert original_file_checksum == received_file_checksum
