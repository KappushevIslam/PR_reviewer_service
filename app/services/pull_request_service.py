import random
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import pull_request as pr_crud
from app.crud import user as user_crud
from app.crud import team as team_crud
from app.schemas.pull_request import PullRequest, PullRequestCreate, PullRequestMerge
from app.schemas.error import ErrorCode
from app.models.pull_request import PRStatus


def create_pull_request_with_reviewers(db: Session, pr_data: PullRequestCreate) -> PullRequest:
    if pr_crud.pr_exists(db, pr_data.pull_request_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": ErrorCode.PR_EXISTS,
                    "message": "PR id already exists"
                }
            }
        )
    
    author = user_crud.get_user(db, pr_data.author_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": ErrorCode.NOT_FOUND,
                    "message": f"Author '{pr_data.author_id}' not found"
                }
            }
        )
    
    team = team_crud.get_team(db, author.team_name)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": ErrorCode.NOT_FOUND,
                    "message": f"Team '{author.team_name}' not found"
                }
            }
        )
    
    try:
        db_pr = pr_crud.create_pull_request(
            db,
            pull_request_id=pr_data.pull_request_id,
            pull_request_name=pr_data.pull_request_name,
            author_id=pr_data.author_id
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
            merged_at=db_pr.merged_at
        )
    
    except Exception as e:
        db.rollback()
        raise e


def merge_pull_request(db: Session, pr_data: PullRequestMerge) -> PullRequest:
    db_pr = pr_crud.get_pull_request(db, pr_data.pull_request_id)
    
    if not db_pr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": ErrorCode.NOT_FOUND,
                    "message": f"PR '{pr_data.pull_request_id}' not found"
                }
            }
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
            merged_at=db_pr.merged_at
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
            merged_at=db_pr.merged_at
        )
    
    except Exception as e:
        db.rollback()
        raise e

