from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pull_request import UserReviewList
from app.schemas.user import UserUpdate
from app.services import pull_request_service, user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/setIsActive", response_model=dict)
def set_user_active(user_data: UserUpdate, db: Session = Depends(get_db)):
    user = user_service.set_user_active_status(db, user_data)
    return {"user": user}


@router.get("/getReview", response_model=UserReviewList)
def get_user_reviews(user_id: str, db: Session = Depends(get_db)):
    return pull_request_service.get_user_reviews(db, user_id)
