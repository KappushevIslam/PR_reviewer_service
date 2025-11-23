import random

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import pull_request as pr_crud
from app.crud import team as team_crud
from app.crud import user as user_crud
from app.models.pull_request import PRStatus
from app.schemas.error import ErrorCode
from app.schemas.pull_request import (
    PullRequest,
    PullRequestCreate,
    PullRequestMerge,
    PullRequestReassign,
    PullRequestShort,
    UserReviewList,
)


def create_pull_request_with_reviewers(db: Session, pr_data: PullRequestCreate) -> PullRequest:
    if pr_crud.pr_exists(db, pr_data.pull_request_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": ErrorCode.PR_EXISTS, "message": "PR id already exists"}},
        )

    author = user_crud.get_user(db, pr_data.author_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": ErrorCode.NOT_FOUND, "message": f"Author '{pr_data.author_id}' not found"}},
        )

    team = team_crud.get_team(db, author.team_name)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": ErrorCode.NOT_FOUND, "message": f"Team '{author.team_name}' not found"}},
        )

    try:
        db_pr = pr_crud.create_pull_request(
            db,
            pull_request_id=pr_data.pull_request_id,
            pull_request_name=pr_data.pull_request_name,
            author_id=pr_data.author_id,
        )

        active_members = [m for m in team.members if m.is_active and m.user_id != pr_data.author_id]

        reviewers_count = min(2, len(active_members))
        if reviewers_count > 0:
            selected_reviewers = random.sample(active_members, reviewers_count)
            for reviewer in selected_reviewers:
                pr_crud.assign_reviewer(db, pr_data.pull_request_id, reviewer.user_id)

        db.commit()
        db.refresh(db_pr)

        assigned_reviewers = pr_crud.get_pr_reviewers(db, pr_data.pull_request_id)

        return PullRequest(
            pull_request_id=db_pr.pull_request_id,
            pull_request_name=db_pr.pull_request_name,
            author_id=db_pr.author_id,
            status=db_pr.status,
            assigned_reviewers=assigned_reviewers,
            created_at=db_pr.created_at,
            merged_at=db_pr.merged_at,
        )

    except Exception as e:
        db.rollback()
        raise e


def merge_pull_request(db: Session, pr_data: PullRequestMerge) -> PullRequest:
    db_pr = pr_crud.get_pull_request(db, pr_data.pull_request_id)

    if not db_pr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": ErrorCode.NOT_FOUND, "message": f"PR '{pr_data.pull_request_id}' not found"}},
        )

    if db_pr.status == PRStatus.MERGED:
        assigned_reviewers = pr_crud.get_pr_reviewers(db, pr_data.pull_request_id)
        return PullRequest(
            pull_request_id=db_pr.pull_request_id,
            pull_request_name=db_pr.pull_request_name,
            author_id=db_pr.author_id,
            status=db_pr.status,
            assigned_reviewers=assigned_reviewers,
            created_at=db_pr.created_at,
            merged_at=db_pr.merged_at,
        )

    try:
        db_pr = pr_crud.merge_pull_request(db, db_pr)
        db.commit()
        db.refresh(db_pr)

        assigned_reviewers = pr_crud.get_pr_reviewers(db, pr_data.pull_request_id)

        return PullRequest(
            pull_request_id=db_pr.pull_request_id,
            pull_request_name=db_pr.pull_request_name,
            author_id=db_pr.author_id,
            status=db_pr.status,
            assigned_reviewers=assigned_reviewers,
            created_at=db_pr.created_at,
            merged_at=db_pr.merged_at,
        )

    except Exception as e:
        db.rollback()
        raise e


def reassign_reviewer(db: Session, reassign_data: PullRequestReassign) -> tuple[PullRequest, str]:
    db_pr = pr_crud.get_pull_request(db, reassign_data.pull_request_id)

    if not db_pr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {"code": ErrorCode.NOT_FOUND, "message": f"PR '{reassign_data.pull_request_id}' not found"}
            },
        )

    if db_pr.status == PRStatus.MERGED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": ErrorCode.PR_MERGED, "message": "cannot reassign on merged PR"}},
        )

    if not pr_crud.is_reviewer_assigned(db, reassign_data.pull_request_id, reassign_data.old_user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": ErrorCode.NOT_ASSIGNED, "message": "reviewer is not assigned to this PR"}},
        )

    old_reviewer = user_crud.get_user(db, reassign_data.old_user_id)
    if not old_reviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {"code": ErrorCode.NOT_FOUND, "message": f"Reviewer '{reassign_data.old_user_id}' not found"}
            },
        )

    team = team_crud.get_team(db, old_reviewer.team_name)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": ErrorCode.NOT_FOUND, "message": f"Team '{old_reviewer.team_name}' not found"}},
        )

    current_reviewers = pr_crud.get_pr_reviewers(db, reassign_data.pull_request_id)

    active_candidates = [
        m for m in team.members if m.is_active and m.user_id != db_pr.author_id and m.user_id not in current_reviewers
    ]

    if not active_candidates:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": ErrorCode.NO_CANDIDATE, "message": "no active replacement candidate in team"}},
        )

    try:
        new_reviewer = random.choice(active_candidates)

        pr_crud.remove_reviewer(db, reassign_data.pull_request_id, reassign_data.old_user_id)
        pr_crud.assign_reviewer(db, reassign_data.pull_request_id, new_reviewer.user_id)

        db.commit()
        db.refresh(db_pr)

        assigned_reviewers = pr_crud.get_pr_reviewers(db, reassign_data.pull_request_id)

        return (
            PullRequest(
                pull_request_id=db_pr.pull_request_id,
                pull_request_name=db_pr.pull_request_name,
                author_id=db_pr.author_id,
                status=db_pr.status,
                assigned_reviewers=assigned_reviewers,
                created_at=db_pr.created_at,
                merged_at=db_pr.merged_at,
            ),
            new_reviewer.user_id,
        )

    except Exception as e:
        db.rollback()
        raise e


def get_user_reviews(db: Session, user_id: str) -> UserReviewList:
    prs = pr_crud.get_user_reviews(db, user_id)

    pr_list = [
        PullRequestShort(
            pull_request_id=pr.pull_request_id,
            pull_request_name=pr.pull_request_name,
            author_id=pr.author_id,
            status=pr.status,
        )
        for pr in prs
    ]

    return UserReviewList(user_id=user_id, pull_requests=pr_list)
