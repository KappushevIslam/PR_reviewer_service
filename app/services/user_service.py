from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import user as user_crud
from app.schemas.user import User, UserUpdate
from app.schemas.error import ErrorCode


def set_user_active_status(db: Session, user_data: UserUpdate) -> User:
    db_user = user_crud.update_user_active_status(db, user_data.user_id, user_data.is_active)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": ErrorCode.NOT_FOUND,
                    "message": f"User '{user_data.user_id}' not found"
                }
            }
        )
    
    try:
        db.commit()
        db.refresh(db_user)
        return User.model_validate(db_user)
    except Exception as e:
        db.rollback()
        raise e

