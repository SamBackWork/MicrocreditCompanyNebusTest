from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas  # Относительный импорт
from ..database import get_db  # Относительный импорт
from ..dependencies import api_key_auth  # Относительный импорт

router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
    dependencies=[Depends(api_key_auth)]
)


@router.get("/", response_model=List[schemas.Activity])
def read_activities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    activities = crud.get_activities(db, skip=skip, limit=limit)
    return activities


@router.get("/{activity_id}", response_model=schemas.Activity)
def read_activity(activity_id: int, db: Session = Depends(get_db)):
    db_activity = crud.get_activity(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return db_activity


@router.post("/", response_model=schemas.Activity, status_code=status.HTTP_201_CREATED)
def create_activity(activity: schemas.ActivityCreate, db: Session = Depends(get_db)):
    return crud.create_activity(db=db, activity=activity)


@router.get("/by_name/{name}", response_model=List[schemas.Activity])
def read_activity_by_name(name: str, db: Session = Depends(get_db)):
    activity = crud.get_activity_by_name(db, name)
    return activity
