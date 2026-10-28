import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# The API module builds its default engine at import time. Keep tests isolated
# from any DATABASE_URL configured on the developer's machine.
os.environ["DATABASE_URL"] = "sqlite://"

from app.database import Base, get_db
from app.main import app
from app.models import Pet, Student


@pytest.fixture
def database() -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_sessions = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    try:
        yield testing_sessions
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def client(database: sessionmaker[Session]) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        db = database()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def student_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "name": "Ana García",
        "email": "ana@example.com",
        "pets": [],
    }
    payload.update(overrides)
    return payload


def test_create_student_and_pet_persist_in_same_request(
    client: TestClient, database: sessionmaker[Session]
) -> None:
    response = client.post(
        "/api/students",
        json=student_payload(pets=[{"name": "Michi", "species": "gato", "age": 3}]),
    )

    assert response.status_code == 201
    student_id = response.json()["data"]["id"]
    with database() as db:
        student = db.get(Student, student_id)
        assert student is not None
        assert [(pet.name, pet.species) for pet in student.pets] == [("Michi", "gato")]


def test_list_students_supports_limit_and_offset(client: TestClient) -> None:
    first = client.post("/api/students", json=student_payload())
    second = client.post(
        "/api/students",
        json=student_payload(name="Beatriz Soto", email="bea@example.com"),
    )
    assert first.status_code == second.status_code == 201

    response = client.get("/api/students?limit=1&offset=1")

    assert response.status_code == 200
    assert len(response.json()["data"]["items"]) == 1


def test_duplicate_email_returns_conflict(client: TestClient) -> None:
    assert client.post("/api/students", json=student_payload()).status_code == 201

    response = client.post(
        "/api/students",
        json=student_payload(name="Otra Persona"),
    )

    assert response.status_code == 409


def test_invalid_email_returns_bad_request(client: TestClient) -> None:
    response = client.post(
        "/api/students",
        json=student_payload(email="no-es-correo"),
    )

    assert response.status_code == 400


def test_missing_student_returns_not_found(client: TestClient) -> None:
    response = client.get("/api/students/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_duplicate_pet_names_do_not_create_student(
    client: TestClient, database: sessionmaker[Session]
) -> None:
    response = client.post(
        "/api/students",
        json=student_payload(
            pets=[
                {"name": "Michi", "species": "gato"},
                {"name": "Michi", "species": "gato"},
            ]
        ),
    )

    assert response.status_code == 409
    with database() as db:
        assert db.query(Student).count() == 0
        assert db.query(Pet).count() == 0


def test_integrity_error_rolls_back_student_and_pet(
    client: TestClient, database: sessionmaker[Session]
) -> None:
    def fail_when_persisting_pet(
        session: Session, flush_context: object, instances: object
    ) -> None:
        if any(isinstance(item, Pet) for item in session.new):
            raise IntegrityError("simulated pet insert failure", {}, RuntimeError())

    event.listen(Session, "before_flush", fail_when_persisting_pet)
    try:
        response = client.post(
            "/api/students",
            json=student_payload(pets=[{"name": "Michi", "species": "gato"}]),
        )
    finally:
        event.remove(Session, "before_flush", fail_when_persisting_pet)

    assert response.status_code == 409
    with database() as db:
        assert db.query(Student).count() == 0
        assert db.query(Pet).count() == 0


def test_zero_limit_returns_bad_request(client: TestClient) -> None:
    response = client.get("/api/students?limit=0")

    assert response.status_code == 400
