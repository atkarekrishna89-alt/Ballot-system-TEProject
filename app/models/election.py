"""Election, Candidate, and Voter models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, UniqueConstraint, Text
from app.core.database import Base


class Election(Base):
    __tablename__ = "elections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="draft")  # draft, active, closed
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self):
        return f"<Election {self.title} [{self.status}]>"


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    election_id = Column(
        String(36), ForeignKey("elections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self):
        return f"<Candidate {self.name}>"


class Voter(Base):
    __tablename__ = "voters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    election_id = Column(
        String(36), ForeignKey("elections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    is_eligible = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "election_id", name="uq_voter_election"),
    )

    def __repr__(self):
        return f"<Voter user={self.user_id} election={self.election_id}>"
