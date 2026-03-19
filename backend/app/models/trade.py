import uuid
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    Numeric,
    Date,
    DateTime,
    Float,
    Text,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models import Base


class Importer(Base):
    """Registered importer/exporter entity."""

    __tablename__ = "importers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    tax_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    country_code: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(Text)
    risk_tier: Mapped[str] = mapped_column(
        String(20), nullable=False, default="standard"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    declarations: Mapped[list["TradeDeclaration"]] = relationship(
        back_populates="importer", lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint(
            "risk_tier IN ('low', 'standard', 'elevated', 'high')",
            name="ck_importer_risk_tier",
        ),
    )


class TradeDeclaration(Base):
    """Single customs trade declaration record."""

    __tablename__ = "trade_declarations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    declaration_number: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False
    )
    importer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("importers.id"), nullable=False
    )
    declaration_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    direction: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # 'import' or 'export'
    origin_country: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    destination_country: Mapped[str] = mapped_column(
        String(3), nullable=False, index=True
    )
    hs_code: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    hs_description: Mapped[str | None] = mapped_column(Text)
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3), nullable=False)
    quantity_unit: Mapped[str] = mapped_column(String(10), nullable=False, default="KG")
    declared_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    transport_mode: Mapped[str | None] = mapped_column(String(20))
    port_of_entry: Mapped[str | None] = mapped_column(String(100))
    is_flagged: Mapped[bool] = mapped_column(default=False)
    flag_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    importer: Mapped["Importer"] = relationship(back_populates="declarations")
    risk_scores: Mapped[list["RiskScore"]] = relationship(
        back_populates="declaration", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_declaration_hs_date", "hs_code", "declaration_date"),
        Index("ix_declaration_origin_dest", "origin_country", "destination_country"),
        CheckConstraint(
            "direction IN ('import', 'export')", name="ck_declaration_direction"
        ),
        CheckConstraint("declared_value >= 0", name="ck_declared_value_positive"),
    )


class RiskScore(Base):
    """Risk assessment score attached to a trade declaration."""

    __tablename__ = "risk_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    declaration_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trade_declarations.id"), nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    rule_code: Mapped[str] = mapped_column(String(50), nullable=False)
    rule_description: Mapped[str | None] = mapped_column(Text)
    is_anomaly: Mapped[bool] = mapped_column(default=False)
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium"
    )
    scored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    declaration: Mapped["TradeDeclaration"] = relationship(back_populates="risk_scores")

    __table_args__ = (
        Index("ix_risk_score_category", "risk_category", "score"),
        CheckConstraint(
            "score >= 0 AND score <= 100", name="ck_risk_score_range"
        ),
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_risk_severity",
        ),
    )
