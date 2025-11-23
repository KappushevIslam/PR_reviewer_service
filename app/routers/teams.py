from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.team import Team, TeamCreate, TeamDeactivateUsers
from app.services import team_service

router = APIRouter(prefix="/team", tags=["Teams"])


@router.post("/add", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    team = team_service.create_team_with_members(db, team_data)
    return {"team": team}


@router.get("/get", response_model=Team)
def get_team(team_name: str, db: Session = Depends(get_db)):
    return team_service.get_team(db, team_name)


@router.post("/deactivateUsers", response_model=dict)
def deactivate_users(deactivate_data: TeamDeactivateUsers, db: Session = Depends(get_db)):
    return team_service.deactivate_users_and_reassign(db, deactivate_data)
