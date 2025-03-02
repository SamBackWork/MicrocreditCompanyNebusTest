from sqlalchemy import Column, Integer, String, ForeignKey, REAL
from sqlalchemy.orm import relationship
from app.database import Base


class Activity(Base):
    """Модель активности."""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    # Связь "один-ко-многим" (родитель-потомки) для иерархии активностей.
    parent = relationship("Activity", remote_side=[id], backref="children")
    # Связь "многие-ко-многим" с организациями через промежуточную таблицу.
    organizations = relationship("Organization", secondary="organization_activities", back_populates="activities")

    def __repr__(self):
        """Строковое представление объекта."""
        return f"<Activity(id={self.id}, name={self.name}, parent_id={self.parent_id})>"


class Building(Base):
    """Модель здания."""
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(255), nullable=False)
    latitude = Column(REAL, nullable=False)
    longitude = Column(REAL, nullable=False)
    # Связь "один-ко-многим" с организациями (здание может содержать несколько организаций).
    organizations = relationship("Organization", back_populates="building")

    def __repr__(self):
        """Строковое представление объекта."""
        return f"<Building(id={self.id}, address={self.address}, latitude={self.latitude}, longitude={self.longitude})>"


class Organization(Base):
    """Модель организации."""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    # Связь "многие-к-одному" со зданием (организация находится в одном здании).
    building = relationship("Building", back_populates="organizations")
    # Связь "один-ко-многим" с телефонами (организация может иметь несколько телефонов).
    phones = relationship("OrganizationPhone", back_populates="organization")
    # Связь "многие-ко-многим" с активностями через промежуточную таблицу.
    activities = relationship("Activity", secondary="organization_activities", back_populates="organizations")

    def __repr__(self):
        """Строковое представление объекта."""
        return f"<Organization(id={self.id}, name={self.name}, building_id={self.building_id})>"


class OrganizationPhone(Base):
    """Модель телефона организации."""
    __tablename__ = "organization_phones"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    phone_number = Column(String(255), nullable=False)
    # Связь "многие-к-одному" с организацией (телефон принадлежит одной организации).
    organization = relationship("Organization", back_populates="phones")

    def __repr__(self):
        """Строковое представление объекта."""
        return f"<OrganizationPhone(id={self.id}, organization_id={self.organization_id}, phone={self.phone_number})>"


class OrganizationActivity(Base):
    """Промежуточная таблица для связи 'многие-ко-многим' между организациями и активностями."""
    __tablename__ = "organization_activities"

    organization_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), primary_key=True)

    def __repr__(self):
        """Строковое представление объекта."""
        return f"<OrganizationActivity(organization_id={self.organization_id}, activity_id={self.activity_id})>"
