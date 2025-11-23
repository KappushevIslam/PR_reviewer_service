from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import team as team_crud
from app.crud import user as user_crud
from app.schemas.team import TeamCreate, Team
from app.schemas.error import ErrorCode


def create_team_with_members(db: Session, team_data: TeamCreate) -> Team:
    if team_crud.team_exists(db, team_data.team_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": ErrorCode.TEAM_EXISTS,
                    "message": "team_name already exists"
                }
            }
        )
    
    try:
        db_team = team_crud.create_team(db, team_data.team_name)
        
        for member in team_data.members:
            existing_user = user_crud.get_user(db, member.user_id)
            if existing_user:
                user_crud.update_user(
                    db,
                    existing_user,
                    username=member.username,
                    is_active=member.is_active
                )
            else:
                user_crud.create_user(
                    db,
                    user_id=member.user_id,
                    username=member.username,
                    team_name=team_data.team_name,
                    is_active=member.is_active
                )
        
        db.commit()
        db.refresh(db_team)
        
        return Team.model_validate(db_team)
    
    except Exception as e:
        db.rollback()
        raise e


def get_team(db: Session, team_name: str) -> Team:
    db_team = team_crud.get_team(db, team_name)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": ErrorCode.NOT_FOUND,
                    "message": f"Team '{team_name}' not found"
                }
            }
        )
    return Team.model_validate(db_team)

