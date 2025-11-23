from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import User, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/setIsActive", response_model=dict)
def set_user_active(user_data: UserUpdate, db: Session = Depends(get_db)):
    user = user_service.set_user_active_status(db, user_data)
    return {"user": user}

