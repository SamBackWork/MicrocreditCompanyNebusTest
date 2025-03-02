from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from . import models, schemas
from typing import List, Optional


# --- Activities ---
def get_activity(db: Session, activity_id: int):
    return db.query(models.Activity).options(joinedload(models.Activity.children)).filter(
        models.Activity.id == activity_id).first()


def get_activities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Activity).options(joinedload(models.Activity.children)).offset(skip).limit(limit).all()


def get_activity_by_name(db: Session, name: str):
    return db.query(models.Activity).filter(models.Activity.name.ilike(f"%{name}%")).all()


def create_activity(db: Session, activity: schemas.ActivityCreate):
    db_activity = models.Activity(**activity.model_dump())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


# --- Buildings ---
def get_building(db: Session, building_id: int):
    return db.query(models.Building).filter(models.Building.id == building_id).first()


def get_buildings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Building).offset(skip).limit(limit).all()


def create_building(db: Session, building: schemas.BuildingCreate):
    db_building = models.Building(**building.model_dump())
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return db_building


# --- Organizations ---
def get_organization(db: Session, organization_id: int):
    return db.query(models.Organization).options(
        joinedload(models.Organization.building),
        joinedload(models.Organization.phones),
        joinedload(models.Organization.activities)
    ).filter(models.Organization.id == organization_id).first()


def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Organization).options(
        joinedload(models.Organization.building),
        joinedload(models.Organization.phones),
        joinedload(models.Organization.activities)
    ).offset(skip).limit(limit).all()


def create_organization(db: Session, organization: schemas.OrganizationCreate):
    db_organization = models.Organization(name=organization.name, building_id=organization.building_id)
    db.add(db_organization)
    db.flush()  # Получаем ID, чтобы использовать его для телефонов и активностей

    for phone in organization.phones:
        db_phone = models.OrganizationPhone(organization_id=db_organization.id, **phone.model_dump())
        db.add(db_phone)

    for activity_id in organization.activities:
        db_activity = models.OrganizationActivity(organization_id=db_organization.id, activity_id=activity_id)
        db.add(db_activity)

    db.commit()
    db.refresh(db_organization)
    return db_organization


def get_organizations_by_building(db: Session, building_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Organization).options(
        joinedload(models.Organization.building),
        joinedload(models.Organization.phones),
        joinedload(models.Organization.activities)
    ).filter(models.Organization.building_id == building_id).offset(skip).limit(limit).all()


def get_organizations_by_activity(db: Session, activity_id: int, skip: int = 0, limit: int = 100,
                                  recursive: bool = False):
    query = db.query(models.Organization).options(
        joinedload(models.Organization.building),
        joinedload(models.Organization.phones),
        joinedload(models.Organization.activities)
    )

    if recursive:
        # Рекурсивный поиск по дереву деятельностей
        activities = [activity_id]
        stack = [activity_id]

        while stack:
            current_activity_id = stack.pop()
            child_activities = db.query(models.Activity.id).filter(
                models.Activity.parent_id == current_activity_id).all()
            for child_activity in child_activities:
                activities.append(child_activity.id)
                stack.append(child_activity.id)

        # Добавим проверку на превышение глубины рекурсии. По ТЗ ограничение - 3 уровня.
        activity_levels = {}  # Словарь для хранения уровней вложенности {id_activity: level}
        activity_levels[activity_id] = 1  # Начинаем с корневой
        level_stack = [activity_id]  # Стэк, для того чтоб узнать предков.
        while level_stack:
            current_act_id = level_stack.pop()
            child_acts = db.query(models.Activity.id, models.Activity.parent_id).filter(
                models.Activity.parent_id == current_act_id).all()
            for child_id, parent_id in child_acts:
                activity_levels[child_id] = activity_levels[current_act_id] + 1
                if activity_levels[child_id] <= 3:  # Проверяем глубину
                    level_stack.append(child_id)
                else:
                    print(f"Превышен лимит вложенности для activity c id {child_id}")

        filtered_activities = [act_id for act_id, level in activity_levels.items() if level <= 3]

        query = query.join(models.OrganizationActivity).filter(
            models.OrganizationActivity.activity_id.in_(filtered_activities))

    else:
        # Поиск только по указанному ID деятельности
        query = query.join(models.OrganizationActivity).filter(models.OrganizationActivity.activity_id == activity_id)

    return query.offset(skip).limit(limit).all()


def get_organizations_within_radius(db: Session, latitude: float, longitude: float, radius: float, skip: int = 0,
                                    limit: int = 100):
    """
    Поиск организаций в заданном радиусе от точки.
    Использует формулу гаверсинусов для расчета расстояния.
    """
    earth_radius_km = 6371  # Радиус Земли в километрах

    subquery = (
        db.query(
            models.Organization.id,
            (
                    earth_radius_km * func.acos(
                func.cos(func.radians(latitude)) *
                func.cos(func.radians(models.Building.latitude)) *
                func.cos(func.radians(models.Building.longitude) - func.radians(longitude)) +
                func.sin(func.radians(latitude)) *
                func.sin(func.radians(models.Building.latitude))
            )
            ).label("distance")
        )
        .join(models.Building)  # Join with Building to access coordinates
        .subquery()
    )

    query = (
        db.query(models.Organization).options(
            joinedload(models.Organization.building),
            joinedload(models.Organization.phones),
            joinedload(models.Organization.activities)
        )
        .join(subquery, models.Organization.id == subquery.c.id)
        .filter(subquery.c.distance <= radius)
        .order_by(subquery.c.distance)  # Сортировка по расстоянию
        .offset(skip)
        .limit(limit)
    )

    return query.all()


def get_organizations_within_rectangle(db: Session, lat_min: float, long_min: float, lat_max: float, long_max: float,
                                       skip: int = 0, limit: int = 100):
    """
    Ищет организации находящиеся в прямоугольнике
    """
    query = (db.query(models.Organization).options(
        joinedload(models.Organization.building),
        joinedload(models.Organization.phones),
        joinedload(models.Organization.activities)
    )
             .join(models.Building)  # Join с таблицей Building
             .filter(
        models.Building.latitude >= lat_min,
        models.Building.latitude <= lat_max,
        models.Building.longitude >= long_min,
        models.Building.longitude <= long_max,
    )
             .offset(skip)
             .limit(limit))

    return query.all()


def get_organization_by_name(db: Session, name: str):
    return (db.query(models.Organization).options(
        joinedload(models.Organization.building),
        joinedload(models.Organization.phones),
        joinedload(models.Organization.activities))
            .filter(models.Organization.name.ilike(f"%{name}%")).all())


# --- Organization Phones ---
def get_phones_by_organization(db: Session, organization_id: int):
    return db.query(models.OrganizationPhone).filter(models.OrganizationPhone.organization_id == organization_id).all()
