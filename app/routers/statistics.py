from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.pull_request import PRStatus, PullRequest, ReviewerAssignment

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("")
def get_statistics(db: Session = Depends(get_db)):
    total_prs = db.query(PullRequest).count()
    open_prs = db.query(PullRequest).filter(PullRequest.status == PRStatus.OPEN).count()
    merged_prs = db.query(PullRequest).filter(PullRequest.status == PRStatus.MERGED).count()

    reviewer_assignments = (
        db.query(ReviewerAssignment.user_id, func.count(ReviewerAssignment.id).label("count"))
        .group_by(ReviewerAssignment.user_id)
        .all()
    )

    assignments_dict = {user_id: count for user_id, count in reviewer_assignments}

    most_active = sorted(reviewer_assignments, key=lambda x: x[1], reverse=True)[:5]
    most_active_reviewers = [{"user_id": user_id, "assignments": count} for user_id, count in most_active]

    return {
        "total_prs": total_prs,
        "open_prs": open_prs,
        "merged_prs": merged_prs,
        "reviewer_assignments": assignments_dict,
        "most_active_reviewers": most_active_reviewers,
    }
