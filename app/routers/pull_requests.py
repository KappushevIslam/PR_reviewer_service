from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pull_request import PullRequest, PullRequestCreate, PullRequestMerge
from app.services import pull_request_service

router = APIRouter(prefix="/pullRequest", tags=["PullRequests"])


@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_pull_request(pr_data: PullRequestCreate, db: Session = Depends(get_db)):
    pr = pull_request_service.create_pull_request_with_reviewers(db, pr_data)
    return {"pr": pr}


@router.post("/merge", response_model=dict)
def merge_pull_request(pr_data: PullRequestMerge, db: Session = Depends(get_db)):
    pr = pull_request_service.merge_pull_request(db, pr_data)
    return {"pr": pr}

