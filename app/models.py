from sqlalchemy import Column, Integer, String, ForeignKey, REAL
from sqlalchemy.orm import relationship
from app.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("activities.id"), nullable=True)

    parent = relationship("Activity", remote_side=[id], backref="children")
    organizations = relationship("Organization", secondary="organization_activities", back_populates="activities")

    def __repr__(self):
        return f"<Activity(id={self.id}, name={self.name}, parent_id={self.parent_id})>"


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(255), nullable=False)
    latitude = Column(REAL, nullable=False)
    longitude = Column(REAL, nullable=False)

    organizations = relationship("Organization", back_populates="building")

    def __repr__(self):
        return f"<Building(id={self.id}, address={self.address}, latitude={self.latitude}, longitude={self.longitude})>"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)

    building = relationship("Building", back_populates="organizations")
    phones = relationship("OrganizationPhone", back_populates="organization")
    activities = relationship("Activity", secondary="organization_activities", back_populates="organizations")

    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name}, building_id={self.building_id})>"


class OrganizationPhone(Base):
    __tablename__ = "organization_phones"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    phone_number = Column(String(255), nullable=False)

    organization = relationship("Organization", back_populates="phones")

    def __repr__(self):
        return f"<OrganizationPhone(id={self.id}, organization_id={self.organization_id}, phone={self.phone_number})>"


class OrganizationActivity(Base):
    __tablename__ = "organization_activities"

    organization_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), primary_key=True)

    def __repr__(self):
        return f"<OrganizationActivity(organization_id={self.organization_id}, activity_id={self.activity_id})>"