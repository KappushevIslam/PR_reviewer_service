from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    team_name = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    members = relationship("User", back_populates="team", cascade="all, delete-orphan")
