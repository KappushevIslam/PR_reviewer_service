from sqlalchemy.orm import Session, joinedload

from app.models.team import Team


def get_team(db: Session, team_name: str) -> Team | None:
    return db.query(Team).options(joinedload(Team.members)).filter(Team.team_name == team_name).first()


def create_team(db: Session, team_name: str) -> Team:
    db_team = Team(team_name=team_name)
    db.add(db_team)
    db.flush()
    return db_team


def team_exists(db: Session, team_name: str) -> bool:
    return db.query(Team).filter(Team.team_name == team_name).first() is not None
