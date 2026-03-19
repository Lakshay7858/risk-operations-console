from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Importer
# ---------------------------------------------------------------------------


class ImporterBase(BaseModel):
    name: str = Field(..., max_length=255)
    tax_id: str = Field(..., max_length=50)
    country_code: str = Field(..., min_length=2, max_length=3)
    address: str | None = None
    risk_tier: str = Field(default="standard", pattern="^(low|standard|elevated|high)$")


class ImporterCreate(ImporterBase):
    pass


class ImporterRead(ImporterBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Trade Declaration
# ---------------------------------------------------------------------------


class TradeDeclarationBase(BaseModel):
    declaration_number: str = Field(..., max_length=30)
    declaration_date: date
    direction: str = Field(..., pattern="^(import|export)$")
    origin_country: str = Field(..., min_length=2, max_length=3)
    destination_country: str = Field(..., min_length=2, max_length=3)
    hs_code: str = Field(..., max_length=12)
    hs_description: str | None = None
    quantity: Decimal = Field(..., ge=0)
    quantity_unit: str = Field(default="KG", max_length=10)
    declared_value: Decimal = Field(..., ge=0)
    currency: str = Field(default="USD", max_length=3)
    weight_kg: float = Field(..., ge=0)
    transport_mode: str | None = None
    port_of_entry: str | None = None


class TradeDeclarationCreate(TradeDeclarationBase):
    importer_id: UUID


class TradeDeclarationRead(TradeDeclarationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    importer_id: UUID
    is_flagged: bool
    flag_reason: str | None = None
    created_at: datetime


class TradeDeclarationDetail(TradeDeclarationRead):
    importer: ImporterRead
    risk_scores: list["RiskScoreRead"] = []


# ---------------------------------------------------------------------------
# Risk Score
# ---------------------------------------------------------------------------


class RiskScoreBase(BaseModel):
    score: float = Field(..., ge=0, le=100)
    risk_category: str = Field(..., max_length=30)
    rule_code: str = Field(..., max_length=50)
    rule_description: str | None = None
    is_anomaly: bool = False
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")


class RiskScoreCreate(RiskScoreBase):
    declaration_id: UUID


class RiskScoreRead(RiskScoreBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    declaration_id: UUID
    scored_at: datetime


# ---------------------------------------------------------------------------
# Analytics Response Schemas
# ---------------------------------------------------------------------------


class VolumePoint(BaseModel):
    """Single data point on a trade volume time series."""
    period: str
    total_declarations: int
    total_value: float
    total_weight: float


class TradeVolumeResponse(BaseModel):
    granularity: str
    data: list[VolumePoint]


class TopTrader(BaseModel):
    importer_id: UUID
    name: str
    country_code: str
    declaration_count: int
    total_value: float
    avg_risk_score: float | None = None


class TopTradersResponse(BaseModel):
    direction: str
    limit: int
    traders: list[TopTrader]


class HSBreakdownItem(BaseModel):
    hs_chapter: str
    description: str | None = None
    declaration_count: int
    total_value: float
    avg_risk_score: float | None = None


class HSBreakdownResponse(BaseModel):
    items: list[HSBreakdownItem]


class AnomalyItem(BaseModel):
    declaration_id: UUID
    declaration_number: str
    declaration_date: date
    score: float
    severity: str
    rule_code: str
    rule_description: str | None = None
    importer_name: str | None = None


class AnomalyResponse(BaseModel):
    total: int
    anomalies: list[AnomalyItem]


class HeatmapCell(BaseModel):
    origin_country: str
    hs_chapter: str
    avg_score: float
    declaration_count: int


class RiskHeatmapResponse(BaseModel):
    cells: list[HeatmapCell]


class RiskDistributionBucket(BaseModel):
    bucket: str
    count: int


class RiskDistributionResponse(BaseModel):
    buckets: list[RiskDistributionBucket]


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[TradeDeclarationRead]
