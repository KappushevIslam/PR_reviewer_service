import enum

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class PRStatus(str, enum.Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"


class PullRequest(Base):
    __tablename__ = "pull_requests"

    pull_request_id = Column(String, primary_key=True, index=True)
    pull_request_name = Column(String, nullable=False)
    author_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    status = Column(SQLEnum(PRStatus), default=PRStatus.OPEN, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    merged_at = Column(DateTime(timezone=True), nullable=True)

    author = relationship("User", foreign_keys=[author_id])
    reviewer_assignments = relationship(
        "ReviewerAssignment", back_populates="pull_request", cascade="all, delete-orphan"
    )


class ReviewerAssignment(Base):
    __tablename__ = "reviewer_assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pull_request_id = Column(
        String, ForeignKey("pull_requests.pull_request_id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    pull_request = relationship("PullRequest", back_populates="reviewer_assignments")
    reviewer = relationship("User")
