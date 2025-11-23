from sqlalchemy.orm import Session, joinedload

from app.models.pull_request import PullRequest, ReviewerAssignment, PRStatus


def get_pull_request(db: Session, pull_request_id: str) -> PullRequest | None:
    return db.query(PullRequest).options(
        joinedload(PullRequest.reviewer_assignments).joinedload(ReviewerAssignment.reviewer)
    ).filter(PullRequest.pull_request_id == pull_request_id).first()


def create_pull_request(db: Session, pull_request_id: str, pull_request_name: str, author_id: str) -> PullRequest:
    db_pr = PullRequest(
        pull_request_id=pull_request_id,
        pull_request_name=pull_request_name,
        author_id=author_id,
        status=PRStatus.OPEN
    )
    db.add(db_pr)
    db.flush()
    return db_pr


def pr_exists(db: Session, pull_request_id: str) -> bool:
    return db.query(PullRequest).filter(PullRequest.pull_request_id == pull_request_id).first() is not None


def assign_reviewer(db: Session, pull_request_id: str, user_id: str) -> ReviewerAssignment:
    assignment = ReviewerAssignment(
        pull_request_id=pull_request_id,
        user_id=user_id
    )
    db.add(assignment)
    db.flush()
    return assignment


def get_pr_reviewers(db: Session, pull_request_id: str) -> list[str]:
    assignments = db.query(ReviewerAssignment).filter(
        ReviewerAssignment.pull_request_id == pull_request_id
    ).all()
    return [a.user_id for a in assignments]


def merge_pull_request(db: Session, pr: PullRequest) -> PullRequest:
    from sqlalchemy.sql import func
    pr.status = PRStatus.MERGED
    pr.merged_at = func.now()
    db.flush()
    return pr

