from datetime import datetime
from pydantic import BaseModel

from app.models.pull_request import PRStatus


class PullRequestCreate(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str


class PullRequestMerge(BaseModel):
    pull_request_id: str


class PullRequestReassign(BaseModel):
    pull_request_id: str
    old_user_id: str


class PullRequest(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus
    assigned_reviewers: list[str]
    created_at: datetime | None = None
    merged_at: datetime | None = None
    
    class Config:
        from_attributes = True


class PullRequestShort(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus
    
    class Config:
        from_attributes = True


class UserReviewList(BaseModel):
    user_id: str
    pull_requests: list[PullRequestShort]

