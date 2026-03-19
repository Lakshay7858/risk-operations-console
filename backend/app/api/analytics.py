from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import get_db
from app.models.trade import TradeDeclaration, RiskScore, Importer
from app.schemas.trade import (
    TradeVolumeResponse,
    VolumePoint,
    TopTradersResponse,
    TopTrader,
    HSBreakdownResponse,
    HSBreakdownItem,
    AnomalyResponse,
    AnomalyItem,
)

router = APIRouter()


@router.get("/volume", response_model=TradeVolumeResponse)
async def trade_volume(
    granularity: str = Query("monthly", pattern="^(daily|weekly|monthly)$"),
    date_from: date | None = None,
    date_to: date | None = None,
    direction: str | None = Query(None, pattern="^(import|export)$"),
    hs_code: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Return trade volume time series aggregated by the requested granularity.
    Supports filtering by date range, direction, and HS code prefix.
    """
    if granularity == "daily":
        period_expr = func.to_char(TradeDeclaration.declaration_date, "YYYY-MM-DD")
    elif granularity == "weekly":
        period_expr = func.to_char(
            func.date_trunc("week", TradeDeclaration.declaration_date), "YYYY-MM-DD"
        )
    else:
        period_expr = func.to_char(TradeDeclaration.declaration_date, "YYYY-MM")

    query = (
        select(
            period_expr.label("period"),
            func.count(TradeDeclaration.id).label("total_declarations"),
            func.coalesce(func.sum(TradeDeclaration.declared_value), 0).label(
                "total_value"
            ),
            func.coalesce(func.sum(TradeDeclaration.weight_kg), 0).label(
                "total_weight"
            ),
        )
        .group_by(period_expr)
        .order_by(period_expr)
    )

    if date_from:
        query = query.where(TradeDeclaration.declaration_date >= date_from)
    if date_to:
        query = query.where(TradeDeclaration.declaration_date <= date_to)
    if direction:
        query = query.where(TradeDeclaration.direction == direction)
    if hs_code:
        query = query.where(TradeDeclaration.hs_code.startswith(hs_code))

    result = await db.execute(query)
    rows = result.all()

    return TradeVolumeResponse(
        granularity=granularity,
        data=[
            VolumePoint(
                period=row.period,
                total_declarations=row.total_declarations,
                total_value=float(row.total_value),
                total_weight=float(row.total_weight),
            )
            for row in rows
        ],
    )


@router.get("/top-traders", response_model=TopTradersResponse)
async def top_traders(
    direction: str = Query("import", pattern="^(import|export)$"),
    limit: int = Query(20, ge=1, le=100),
    date_from: date | None = None,
    date_to: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Return the top importers or exporters ranked by total declared value.
    Includes declaration count and average risk score.
    """
    avg_risk = (
        select(func.avg(RiskScore.score))
        .where(RiskScore.declaration_id == TradeDeclaration.id)
        .correlate(TradeDeclaration)
        .scalar_subquery()
    )

    query = (
        select(
            Importer.id.label("importer_id"),
            Importer.name,
            Importer.country_code,
            func.count(TradeDeclaration.id).label("declaration_count"),
            func.sum(TradeDeclaration.declared_value).label("total_value"),
            avg_risk.label("avg_risk_score"),
        )
        .join(TradeDeclaration, TradeDeclaration.importer_id == Importer.id)
        .where(TradeDeclaration.direction == direction)
        .group_by(Importer.id, Importer.name, Importer.country_code)
        .order_by(func.sum(TradeDeclaration.declared_value).desc())
        .limit(limit)
    )

    if date_from:
        query = query.where(TradeDeclaration.declaration_date >= date_from)
    if date_to:
        query = query.where(TradeDeclaration.declaration_date <= date_to)

    result = await db.execute(query)
    rows = result.all()

    return TopTradersResponse(
        direction=direction,
        limit=limit,
        traders=[
            TopTrader(
                importer_id=row.importer_id,
                name=row.name,
                country_code=row.country_code,
                declaration_count=row.declaration_count,
                total_value=float(row.total_value),
                avg_risk_score=float(row.avg_risk_score) if row.avg_risk_score else None,
            )
            for row in rows
        ],
    )


@router.get("/hs-breakdown", response_model=HSBreakdownResponse)
async def hs_breakdown(
    date_from: date | None = None,
    date_to: date | None = None,
    direction: str | None = Query(None, pattern="^(import|export)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Break down trade activity by HS code chapter (first 2 digits).
    Returns declaration counts, total value, and average risk score per chapter.
    """
    hs_chapter = func.substr(TradeDeclaration.hs_code, 1, 2).label("hs_chapter")

    avg_risk = (
        select(func.avg(RiskScore.score))
        .where(RiskScore.declaration_id == TradeDeclaration.id)
        .correlate(TradeDeclaration)
        .scalar_subquery()
    )

    query = (
        select(
            hs_chapter,
            func.count(TradeDeclaration.id).label("declaration_count"),
            func.sum(TradeDeclaration.declared_value).label("total_value"),
            func.avg(avg_risk).label("avg_risk_score"),
        )
        .group_by(hs_chapter)
        .order_by(func.sum(TradeDeclaration.declared_value).desc())
    )

    if date_from:
        query = query.where(TradeDeclaration.declaration_date >= date_from)
    if date_to:
        query = query.where(TradeDeclaration.declaration_date <= date_to)
    if direction:
        query = query.where(TradeDeclaration.direction == direction)

    result = await db.execute(query)
    rows = result.all()

    return HSBreakdownResponse(
        items=[
            HSBreakdownItem(
                hs_chapter=row.hs_chapter,
                declaration_count=row.declaration_count,
                total_value=float(row.total_value),
                avg_risk_score=float(row.avg_risk_score) if row.avg_risk_score else None,
            )
            for row in rows
        ]
    )


@router.get("/anomalies", response_model=AnomalyResponse)
async def anomalies(
    date_from: date | None = None,
    date_to: date | None = None,
    min_severity: str = Query("medium", pattern="^(low|medium|high|critical)$"),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Return detected anomalies ordered by score descending.
    Filters by date range and minimum severity level.
    """
    severity_order = case(
        (RiskScore.severity == "critical", 4),
        (RiskScore.severity == "high", 3),
        (RiskScore.severity == "medium", 2),
        (RiskScore.severity == "low", 1),
        else_=0,
    )

    min_severity_val = {"low": 1, "medium": 2, "high": 3, "critical": 4}[min_severity]

    query = (
        select(
            TradeDeclaration.id.label("declaration_id"),
            TradeDeclaration.declaration_number,
            TradeDeclaration.declaration_date,
            RiskScore.score,
            RiskScore.severity,
            RiskScore.rule_code,
            RiskScore.rule_description,
            Importer.name.label("importer_name"),
        )
        .join(RiskScore, RiskScore.declaration_id == TradeDeclaration.id)
        .join(Importer, Importer.id == TradeDeclaration.importer_id)
        .where(RiskScore.is_anomaly.is_(True))
        .where(severity_order >= min_severity_val)
        .order_by(RiskScore.score.desc())
        .limit(limit)
    )

    if date_from:
        query = query.where(TradeDeclaration.declaration_date >= date_from)
    if date_to:
        query = query.where(TradeDeclaration.declaration_date <= date_to)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    result = await db.execute(query)
    rows = result.all()

    return AnomalyResponse(
        total=total,
        anomalies=[
            AnomalyItem(
                declaration_id=row.declaration_id,
                declaration_number=row.declaration_number,
                declaration_date=row.declaration_date,
                score=row.score,
                severity=row.severity,
                rule_code=row.rule_code,
                rule_description=row.rule_description,
                importer_name=row.importer_name,
            )
            for row in rows
        ],
    )
