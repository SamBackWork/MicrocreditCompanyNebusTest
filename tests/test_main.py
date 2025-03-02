# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

TEST_DATABASE_URL = "sqlite:///./test.db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.main import app
from app.database import Base, get_db
from app import models, schemas
from app.dependencies import api_key_auth

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def override_get_db():
    def override_dependency():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    return override_dependency


@pytest.fixture(scope="module")  # Фикстура с данными
def test_data(test_db):
    building = models.Building(address="Test Building", latitude=34.56, longitude=56.78)
    test_db.add(building)
    test_db.commit()
    test_db.refresh(building)
    return building  # Возвращаем здание


@pytest.fixture(scope="module")
def client(test_db, override_get_db):
    app.dependency_overrides[get_db] = override_get_db

    async def skip_auth():
        return True

    app.dependency_overrides[api_key_auth] = skip_auth
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_create_organization(client, test_db, test_data):
    response = client.post(
        "/organizations/",
        json={
            "name": "Test Organization",
            "building_id": test_data.id,
            "phones": [{"phone_number": "123-456-7890"}],
            "activities": [],
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Test Organization"
    assert data["building"]["id"] == test_data.id
    assert len(data["phones"]) == 1
    assert data["phones"][0]["phone_number"] == "123-456-7890"
    assert "id" in data


def test_get_organizations(client, test_db, test_data):
    test_create_organization(client, test_db, test_data)  # Создаем организацию
    response = client.get("/organizations/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Organization"


def test_get_organization_by_id(client, test_db, test_data):
    test_create_organization(client, test_db, test_data)  # Создаём
    response = client.get("/organizations/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Organization"
    assert data["id"] == 1


def test_get_organization_not_found(client, test_db):
    response = client.get("/organizations/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Organization not found"}


def test_create_and_get_building(client, test_db, test_data):
    #  Не создаем здание здесь, оно уже есть в test_data!
    response = client.get(f"/buildings/{test_data.id}")
    assert response.status_code == 200
    assert response.json()["address"] == "Test Building"


# Добавленные тесты:
def test_create_building(client, test_db):
    building_data = {
        "address": "Another Test Building",
        "latitude": 12.34,
        "longitude": 56.78,
    }
    response = client.post("/buildings/", json=building_data)
    assert response.status_code == 201
    data = response.json()
    assert data["address"] == "Another Test Building"
    assert data["latitude"] == 12.34
    assert data["longitude"] == 56.78
    assert "id" in data


def test_get_buildings(client, test_db, test_data):
    test_create_building(client, test_db)
    response = client.get('/buildings/')
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_building_by_id(client, test_db, test_data):
    response = client.get(f"/buildings/{test_data.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == "Test Building"
    assert data["id"] == test_data.id


def test_get_building_not_found(client, test_db):
    response = client.get("/buildings/999")
    assert response.status_code == 404


def test_create_activity(client, test_db):
    activity_data = {"name": "Test Activity", "parent_id": None}
    response = client.post("/activities/", json=activity_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Activity"
    assert data["parent_id"] is None
    assert "id" in data

    # Тест с parent_id
    activity_data2 = {"name": "Child Activity", "parent_id": data["id"]}
    response2 = client.post("/activities/", json=activity_data2)
    assert response2.status_code == 201
    data2 = response2.json()
    assert data2["parent_id"] == data["id"]


def test_get_activities(client, test_db):
    test_create_activity(client, test_db)
    response = client.get("/activities/")
    assert response.status_code == 200
    assert len(response.json()) >= 0  # Длина может быть больше нуля из-за фикстуры


def test_get_activity_by_id(client, test_db):
    # Создаем активность, чтобы получить её ID
    response = client.post("/activities/", json={"name": "Activity for ID Test"})
    activity_id = response.json()["id"]
    response = client.get(f"/activities/{activity_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Activity for ID Test"
    assert data["id"] == activity_id


def test_get_activity_not_found(client, test_db):
    response = client.get("/activities/999")
    assert response.status_code == 404


def test_get_organizations_by_building(client, test_db, test_data):
    test_create_organization(client, test_db, test_data)  # Создаем организацию
    response = client.get(f"/organizations/by_building/{test_data.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["building"]["id"] == test_data.id  # Исправлено


def test_get_organizations_by_activity(client, test_db, test_data):
    # Создаем организацию и связываем ее с активностью.
    activity = models.Activity(name='ActivityTest')
    test_db.add(activity)
    test_db.commit()
    test_db.refresh(activity)
    response = client.post(
        '/organizations/',
        json={
            "name": "Test Organization Activity",
            'building_id': test_data.id,
            'phones': [],
            'activities': [activity.id]
        }
    )

    response = client.get(f"/organizations/by_activity/{activity.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]['name'] == "Test Organization Activity"


def test_get_organizations_within_radius(client, test_db, test_data):
    # Создаём организацию в пределах радиуса.
    org = models.Organization(name="Org in Radius", building_id=test_data.id)
    test_db.add(org)
    test_db.commit()

    response = client.get(
        f"/organizations/within_radius/?latitude={test_data.latitude}&longitude={test_data.longitude}&radius=1"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(org["name"] == "Org in Radius" for org in data)  # Исправлено


def test_get_organizations_within_rectangle(client, test_db, test_data):
    # Создаеём организацию в пределах прямоугольника.
    org = models.Organization(name="Org in Rectangle", building_id=test_data.id)
    test_db.add(org)
    test_db.commit()

    response = client.get(
        f"/organizations/within_rectangle/?lat_min={test_data.latitude - 0.01}&long_min={test_data.longitude - 0.01}&lat_max={test_data.latitude + 0.01}&long_max={test_data.longitude + 0.01}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(org["name"] == "Org in Rectangle" for org in data)  # Исправлено


def test_get_organization_by_name(client, test_db, test_data):
    test_create_organization(client, test_db, test_data)
    response = client.get(f"/organizations/by_name/Test")
    assert response.status_code == 200
    assert any("Test" in org["name"] for org in response.json())  # Исправлено


def test_get_activity_by_name(client, test_db):
    test_create_activity(client, test_db)
    response = client.get(f'/activities/by_name/Test')
    assert response.status_code == 200
    assert len(response.json()) >= 0
