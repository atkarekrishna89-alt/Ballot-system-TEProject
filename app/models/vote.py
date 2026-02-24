"""Vote model — anonymous, no user_id stored."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from app.core.database import Base


class Vote(Base):
    __tablename__ = "votes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    election_id = Column(
        String(36), ForeignKey("elections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_id = Column(
        String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hashed_voter_token = Column(String(64), nullable=False, index=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # CRITICAL: Unique constraint prevents duplicate votes per election
    __table_args__ = (
        UniqueConstraint("election_id", "hashed_voter_token", name="uq_vote_election_token"),
    )

    def __repr__(self):
        return f"<Vote election={self.election_id}>"
