from pydantic import BaseModel, Field, validator, ConfigDict  # Импортируем ConfigDict
from typing import List, Optional
from pydantic import constr


class ActivityBase(BaseModel):
    """Базовая схема для активностей."""
    name: constr(min_length=1, max_length=255)  # Ограничение длины строки
    parent_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    """Схема для создания активности."""
    pass


class Activity(ActivityBase):
    """Схема для чтения активности, включая вложенные дочерние активности."""
    id: int
    children: List['Activity'] = []  # Рекурсивное определение для вложенных активностей

    model_config = ConfigDict(from_attributes=True)  # Включить поддержку ORM


# Необходимо для рекурсивного определения (ForwardRef) и избежания ошибок.
Activity.model_rebuild()


class BuildingBase(BaseModel):
    """Базовая схема для зданий."""
    address: constr(min_length=1, max_length=255)  # Ограничение длины строки
    latitude: float = Field(..., ge=-90, le=90)  # Ограничения для широты
    longitude: float = Field(..., ge=-180, le=180)  # Ограничения для долготы


class BuildingCreate(BuildingBase):
    """Схема для создания здания."""
    pass


class Building(BuildingBase):
    """Схема для чтения здания."""
    id: int
    model_config = ConfigDict(from_attributes=True)  # Правильно


class OrganizationPhoneBase(BaseModel):
    """Базовая схема для телефонов организаций."""
    phone_number: constr(min_length=5, max_length=20)  # Ограничение длины строки


class OrganizationPhoneCreate(OrganizationPhoneBase):
    """Схема для создания телефона организации."""
    pass


class OrganizationPhone(OrganizationPhoneBase):
    """Схема для чтения телефона организации."""
    id: int
    organization_id: int
    model_config = ConfigDict(from_attributes=True)  # Правильно


class OrganizationBase(BaseModel):
    """Базовая схема для организаций."""
    name: constr(min_length=1, max_length=255)  # Ограничение длины строки


class OrganizationCreate(OrganizationBase):
    """Схема для создания организации."""
    building_id: int
    phones: List[OrganizationPhoneCreate]
    activities: List[int] = []  # Список ID активностей


class Organization(OrganizationBase):
    """Схема для чтения организации, включая связанные данные."""
    id: int
    building: Building  # Вложенное здание
    phones: List[OrganizationPhone]  # Вложенные телефоны
    activities: List[Activity]  # Вложенные активности
    model_config = ConfigDict(from_attributes=True)  # Правильно
