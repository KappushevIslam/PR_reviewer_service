import random

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import pull_request as pr_crud
from app.crud import team as team_crud
from app.crud import user as user_crud
from app.models.pull_request import PRStatus
from app.schemas.error import ErrorCode
from app.schemas.team import Team, TeamCreate, TeamDeactivateUsers


def create_team_with_members(db: Session, team_data: TeamCreate) -> Team:
    if team_crud.team_exists(db, team_data.team_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": ErrorCode.TEAM_EXISTS, "message": "team_name already exists"}},
        )

    try:
        db_team = team_crud.create_team(db, team_data.team_name)

        for member in team_data.members:
            existing_user = user_crud.get_user(db, member.user_id)
            if existing_user:
                user_crud.update_user(db, existing_user, username=member.username, is_active=member.is_active)
            else:
                user_crud.create_user(
                    db,
                    user_id=member.user_id,
                    username=member.username,
                    team_name=team_data.team_name,
                    is_active=member.is_active,
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
            detail={"error": {"code": ErrorCode.NOT_FOUND, "message": f"Team '{team_name}' not found"}},
        )
    return Team.model_validate(db_team)


def deactivate_users_and_reassign(db: Session, deactivate_data: TeamDeactivateUsers) -> dict:
    team = team_crud.get_team(db, deactivate_data.team_name)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": ErrorCode.NOT_FOUND, "message": f"Team '{deactivate_data.team_name}' not found"}},
        )

    try:
        deactivated_count = 0
        reassigned_count = 0

        for user_id in deactivate_data.user_ids:
            user = user_crud.get_user(db, user_id)
            if user and user.team_name == deactivate_data.team_name:
                user_crud.update_user_active_status(db, user_id, False)
                deactivated_count += 1

                open_prs_with_user = (
                    db.query(pr_crud.PullRequest)
                    .join(pr_crud.ReviewerAssignment)
                    .filter(pr_crud.ReviewerAssignment.user_id == user_id, pr_crud.PullRequest.status == PRStatus.OPEN)
                    .all()
                )

                for pr in open_prs_with_user:
                    current_reviewers = pr_crud.get_pr_reviewers(db, pr.pull_request_id)
                    active_candidates = [
                        m
                        for m in team.members
                        if m.is_active
                        and m.user_id != pr.author_id
                        and m.user_id not in current_reviewers
                        and m.user_id not in deactivate_data.user_ids
                    ]

                    if active_candidates:
                        new_reviewer = random.choice(active_candidates)
                        pr_crud.remove_reviewer(db, pr.pull_request_id, user_id)
                        pr_crud.assign_reviewer(db, pr.pull_request_id, new_reviewer.user_id)
                        reassigned_count += 1
                    else:
                        pr_crud.remove_reviewer(db, pr.pull_request_id, user_id)

        db.commit()

        return {"deactivated_users": deactivated_count, "reassigned_prs": reassigned_count}

    except Exception as e:
        db.rollback()
        raise e
