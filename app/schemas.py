# app/schemas.py
from pydantic import BaseModel, Field, validator, ConfigDict  # Импортируем ConfigDict
from typing import List, Optional
from pydantic import constr


class ActivityBase(BaseModel):
    name: constr(min_length=1, max_length=255)
    parent_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    pass


class Activity(ActivityBase):
    id: int
    children: List['Activity'] = []

    model_config = ConfigDict(from_attributes=True)


Activity.model_rebuild()


class BuildingBase(BaseModel):
    address: constr(min_length=1, max_length=255)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class BuildingCreate(BuildingBase):
    pass


class Building(BuildingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # Правильно


class OrganizationPhoneBase(BaseModel):
    phone_number: constr(min_length=5, max_length=20)


class OrganizationPhoneCreate(OrganizationPhoneBase):
    pass


class OrganizationPhone(OrganizationPhoneBase):
    id: int
    organization_id: int

    model_config = ConfigDict(from_attributes=True)  # Правильно


class OrganizationBase(BaseModel):
    name: constr(min_length=1, max_length=255)


class OrganizationCreate(OrganizationBase):
    building_id: int
    phones: List[OrganizationPhoneCreate]
    activities: List[int] = []


class Organization(OrganizationBase):
    id: int
    building: Building
    phones: List[OrganizationPhone]
    activities: List[Activity]

    model_config = ConfigDict(from_attributes=True)  # Правильно
