from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class DealStage(StrEnum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class LeadSource(StrEnum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    REFERRAL = "referral"
    PARTNER = "partner"
    EVENT = "event"
    WEBSITE = "website"
    OTHER = "other"


class Industry(StrEnum):
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    REAL_ESTATE = "real_estate"
    OTHER = "other"


# ---------------------------------------------------------------------------
# Deal schemas
# ---------------------------------------------------------------------------


class DealBase(BaseModel):
    """Fields shared across create / read / update."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
    )

    deal_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Human-readable name of the deal.",
        examples=["Acme Corp — Enterprise Licence Q4"],
    )
    company: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the prospect or customer company.",
        examples=["Acme Corp"],
    )
    value: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Monetary value of the deal in the account's base currency.",
        examples=[150000.00],
    )
    stage: DealStage = Field(
        ...,
        description="Current pipeline stage of the deal.",
        examples=[DealStage.PROPOSAL],
    )
    owner: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Full name or identifier of the sales rep who owns the deal.",
        examples=["Jane Smith"],
    )
    last_activity_date: date = Field(
        ...,
        description="ISO-8601 date of the most recent activity on this deal.",
        examples=["2024-11-15"],
    )
    lead_source: LeadSource = Field(
        ...,
        description="Channel through which this lead was acquired.",
        examples=[LeadSource.INBOUND],
    )
    industry: Industry = Field(
        ...,
        description="Industry vertical of the prospect company.",
        examples=[Industry.TECHNOLOGY],
    )
    days_in_stage: int = Field(
        ...,
        ge=0,
        description="Number of calendar days the deal has been in its current stage.",
        examples=[14],
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Free-text notes or context about the deal.",
        examples=["Champion is VP of Engineering. Budget approved for Q1."],
    )

    @field_validator("value", mode="before")
    @classmethod
    def coerce_value(cls, v: object) -> Decimal:
        """Accept int / float / str and coerce to Decimal."""
        if isinstance(v, Decimal):
            return v
        try:
            return Decimal(str(v))
        except Exception as exc:
            raise ValueError(f"Invalid deal value: {v!r}") from exc


class DealCreate(DealBase):
    """Schema for creating a new deal (no server-generated fields)."""


class DealRead(DealBase):
    """Schema for reading a deal returned from the API (includes server fields)."""

    id: str = Field(
        ...,
        description="Unique identifier of the deal.",
        examples=["deal_01J9ZX"],
    )

    model_config = ConfigDict(from_attributes=True)


class DealUpdate(BaseModel):
    """Partial-update schema — all fields optional."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
    )

    deal_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    company: Optional[str] = Field(default=None, min_length=1, max_length=255)
    value: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    stage: Optional[DealStage] = None
    owner: Optional[str] = Field(default=None, min_length=1, max_length=255)
    last_activity_date: Optional[date] = None
    lead_source: Optional[LeadSource] = None
    industry: Optional[Industry] = None
    days_in_stage: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = Field(default=None, max_length=5000)