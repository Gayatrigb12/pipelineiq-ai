from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ---------------------------------------------------------------------------
# Declarative base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Project-wide SQLAlchemy declarative base."""


# ---------------------------------------------------------------------------
# Deal model
# ---------------------------------------------------------------------------


class Deal(Base):
    """ORM representation of a CRM deal stored in the ``deals`` table."""

    __tablename__ = "deals"

    # ------------------------------------------------------------------
    # Primary key
    # ------------------------------------------------------------------

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Core deal fields
    # ------------------------------------------------------------------

    deal_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="USD",
        server_default="USD",
    )
    stage: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    owner: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Classification / source
    # ------------------------------------------------------------------

    lead_source: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    industry: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Contact info
    # ------------------------------------------------------------------

    contact_person: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    contact_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Timeline / activity
    # ------------------------------------------------------------------

    last_activity_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    days_in_stage: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    expected_close_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Free-text
    # ------------------------------------------------------------------

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Audit timestamps
    # ------------------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Deal("
            f"id={self.id!r}, "
            f"deal_name={self.deal_name!r}, "
            f"company={self.company!r}, "
            f"stage={self.stage!r}, "
            f"value={self.value!r}, "
            f"owner={self.owner!r}"
            f")"
        )