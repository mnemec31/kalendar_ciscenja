import pytest
import hashlib
import datetime

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models.users import User, UserCreate
from app.security import get_password_hash, create_access_token


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


@pytest.fixture(name="user")
def user_fixture(session: Session):
    password = "pass1234"
    user = User(
        username="test_user",
        hashed_password=get_password_hash(password),
    )

    session.add(user)
    session.commit()

    session.refresh(user)
    yield UserCreate(username=user.username, password=password)

    session.delete(user)
    session.commit()


@pytest.fixture(name="auth_headers")
def logged_in_user_fixture(session: Session):
    password = "pass1234"
    user = User(
        username="test_user",
        hashed_password=get_password_hash(password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=datetime.timedelta(10),
    )

    yield {"Authorization": f"Bearer {access_token}"}

    session.delete(user)
    session.commit()


TEST_FILES_PATH = "app/tests/test_files"


def test_get_token_not_auth(client: TestClient):
    response = client.post("/token")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_token(client: TestClient, user: UserCreate):
    login_payload = {"username": user.username, "password": user.password}
    response = client.post("/token", data=login_payload)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_get_calendars_not_auth(client: TestClient):
    response = client.get("/calendars")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_calendars(client: TestClient, auth_headers: dict):
    response = client.get("/calendars", headers=auth_headers)

    data = response.json()
    assert data == []
    assert response.status_code == status.HTTP_200_OK


def test_upload_calendar_not_auth(client: TestClient):
    with open(f"{TEST_FILES_PATH}/valid/apartment_1.ics", "rb") as f:
        response = client.post(
            "/import-calendar",
            files={"file": f},
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_import_calendar_not_auth(client: TestClient):
    calendar_url = (
        "https://www.phpclasses.org/browse/download/1/file/63438/name/example.ics"
    )

    response = client.post(
        "/import-from-url",
        json={"url": calendar_url},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_upload_calendar_valid(client: TestClient, auth_headers: dict):
    with open(f"{TEST_FILES_PATH}/valid/apartment_1.ics", "rb") as f:
        response = client.post(
            "/import-calendar",
            headers=auth_headers,
            files={"file": f},
        )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["name"] == "primjer zadatka - apartment 1"

    for event in data["events"]:
        del event["id"]

    assert data["events"] == [
        {
            "uid": "aca171cfaa8cf1c5765e64e819906485",
            "summary": "Ivica",
            "date_start": "2020-09-30",
            "date_end": "2020-10-02",
        },
        {
            "uid": "26db1820702b397cc969489412b44f6a",
            "summary": "Jurica",
            "date_start": "2020-10-04",
            "date_end": "2020-10-10",
        },
    ]


def test_upload_calendar_invalid(client: TestClient, auth_headers: dict):
    INVALID_FILES_LIST = [
        "empty.ics",
        "event_no_start_and_end.ics",
        "events_conflict.ics",
        "events_same_end.ics",
        "events_same_start.ics",
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
                headers=auth_headers,
                files={"file": f},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_and_download(client: TestClient, auth_headers: dict):
    with open(f"{TEST_FILES_PATH}/valid/apartment_1.ics", "rb") as f:
        original_file_checksum = hashlib.md5(f.read()).hexdigest()

        response = client.post(
            "/import-calendar",
            headers=auth_headers,
            files={"file": f},
        )

    assert response.status_code == status.HTTP_200_OK

    response = client.get("/calendars/1", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    received_file_checksum = hashlib.md5(response.read()).hexdigest()
    assert original_file_checksum == received_file_checksum


def test_import_from_url_invalid_url(client: TestClient, auth_headers: dict):
    response = client.post(
        "/import-from-url", headers=auth_headers, json={"url": "blabla"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_import_from_url_no_ics_file_on_url(client: TestClient, auth_headers: dict):
    response = client.post(
        "/import-from-url", headers=auth_headers, json={"url": "https:://www.google.hr"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_import_from_url_valid(client: TestClient, auth_headers: dict):
    calendar_url = (
        "https://www.phpclasses.org/browse/download/1/file/63438/name/example.ics"
    )

    response = client.post(
        "/import-from-url",
        headers=auth_headers,
        json={"url": calendar_url},
    )

    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["name"] == "-//Mozilla.org/NONSGML Mozilla Calendar V1.1//EN"
    assert data["url"] == calendar_url

    for event in data["events"]:
        del event["id"]

    assert data["events"] == [
        {
            "uid": "20f78720-d755-4de7-92e5-e41af487e4db",
            "summary": "Just a Test",
            "date_start": "2014-01-02",
            "date_end": "2014-01-02",
        }
    ]
