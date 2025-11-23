from sqlalchemy.orm import Session

from app.models.user import User


def get_user(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()


def create_user(db: Session, user_id: str, username: str, team_name: str, is_active: bool) -> User:
    db_user = User(user_id=user_id, username=username, team_name=team_name, is_active=is_active)
    db.add(db_user)
    db.flush()
    return db_user


def update_user(db: Session, user: User, username: str = None, is_active: bool = None) -> User:
    if username is not None:
        user.username = username
    if is_active is not None:
        user.is_active = is_active
    db.flush()
    return user


def update_user_active_status(db: Session, user_id: str, is_active: bool) -> User | None:
    user = get_user(db, user_id)
    if user:
        user.is_active = is_active
        db.flush()
    return user
