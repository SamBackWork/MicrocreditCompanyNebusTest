from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models  # Относительный импорт
from ..database import get_db  # Относительный импорт
from ..dependencies import api_key_auth  # Относительный импорт

# Создаем роутер для организаций.
router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
    dependencies=[Depends(api_key_auth)]  # Добавляем зависимость для аутентификации
)


@router.get("/", response_model=List[schemas.Organization])
def read_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получает список всех организаций с возможностью пагинации.
    """
    organizations = crud.get_organizations(db, skip=skip, limit=limit)
    return organizations


@router.get("/{organization_id}", response_model=schemas.Organization)
def read_organization(organization_id: int, db: Session = Depends(get_db)):
    """
    Получает информацию об организации по её ID.
    """
    db_organization = crud.get_organization(db, organization_id=organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization


@router.post("/", response_model=schemas.Organization, status_code=201)
def create_organization(organization: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    """
    Создает новую организацию.
    """
    return crud.create_organization(db=db, organization=organization)


@router.get("/by_building/{building_id}", response_model=List[schemas.Organization])
def read_organizations_by_building(building_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получает список организаций, связанных с определенным зданием, с пагинацией.
    """
    organizations = crud.get_organizations_by_building(db, building_id=building_id, skip=skip, limit=limit)
    return organizations


@router.get("/by_activity/{activity_id}", response_model=List[schemas.Organization])
def read_organizations_by_activity(activity_id: int, recursive: bool = False, skip: int = 0, limit: int = 100,
                                   db: Session = Depends(get_db)):
    """
    Получает список организаций, связанных с определенной активностью.

    Args:
        activity_id: ID активности.
        recursive: Если True, ищет организации, связанные с дочерними активностями (до 3 уровня вложенности).
        skip: Смещение для пагинации.
        limit: Предел для пагинации.
        db: Сессия базы данных.
    """
    organizations = crud.get_organizations_by_activity(db, activity_id=activity_id, skip=skip, limit=limit,
                                                       recursive=recursive)
    return organizations


@router.get("/within_radius/", response_model=List[schemas.Organization])
def read_organizations_within_radius(
        latitude: float = Query(..., description="Latitude of the center point"),
        longitude: float = Query(..., description="Longitude of the center point"),
        radius: float = Query(..., description="Radius in kilometers"),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """
    Получает список организаций, находящихся в заданном радиусе от указанной точки.
    Используется формула гаверсинусов для расчета расстояния.

    """
    organizations = crud.get_organizations_within_radius(db, latitude=latitude, longitude=longitude, radius=radius,
                                                         skip=skip, limit=limit)
    return organizations


@router.get("/within_rectangle/", response_model=List[schemas.Organization])
def read_organizations_within_rectangle(
        lat_min: float = Query(..., description="Minimum latitude"),
        long_min: float = Query(..., description="Minimum longitude"),
        lat_max: float = Query(..., description="Maximum latitude"),
        long_max: float = Query(..., description="Maximum longitude"),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """
     Получает список организаций, находящихся в пределах заданного прямоугольника.
    """
    organizations = crud.get_organizations_within_rectangle(db, lat_min, long_min, lat_max, long_max, skip, limit)
    return organizations


@router.get("/by_name/{name}", response_model=List[schemas.Organization])
def read_organizations_by_name(name: str, db: Session = Depends(get_db)):
    """Получает организации, имя которых содержит заданную подстроку."""
    organizations = crud.get_organization_by_name(db, name)
    return organizations
