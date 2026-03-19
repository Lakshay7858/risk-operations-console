from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import get_db
from app.models.trade import TradeDeclaration, RiskScore
from app.schemas.trade import (
    RiskScoreCreate,
    RiskScoreRead,
    RiskHeatmapResponse,
    HeatmapCell,
    RiskDistributionResponse,
    RiskDistributionBucket,
)

router = APIRouter()


@router.get("/scores", response_model=list[RiskScoreRead])
async def list_risk_scores(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    risk_category: str | None = None,
    min_score: float | None = Query(None, ge=0, le=100),
    declaration_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List risk scores with optional filtering by category, minimum score, or declaration."""
    query = select(RiskScore)

    if risk_category:
        query = query.where(RiskScore.risk_category == risk_category)
    if min_score is not None:
        query = query.where(RiskScore.score >= min_score)
    if declaration_id:
        query = query.where(RiskScore.declaration_id == declaration_id)

    query = (
        query.order_by(RiskScore.score.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    scores = result.scalars().all()

    return [RiskScoreRead.model_validate(s) for s in scores]


@router.post("/scores", response_model=RiskScoreRead, status_code=201)
async def create_risk_score(
    payload: RiskScoreCreate,
    db: AsyncSession = Depends(get_db),
):
    """Record a new risk score for a trade declaration."""
    score = RiskScore(**payload.model_dump())
    db.add(score)
    await db.commit()
    await db.refresh(score)

    return RiskScoreRead.model_validate(score)


@router.get("/heatmap", response_model=RiskHeatmapResponse)
async def risk_heatmap(
    date_from: date | None = None,
    date_to: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a risk heatmap with average scores bucketed by origin country
    and HS code chapter (first 2 digits). Used to visualize risk corridors.
    """
    hs_chapter = func.substr(TradeDeclaration.hs_code, 1, 2).label("hs_chapter")

    query = (
        select(
            TradeDeclaration.origin_country,
            hs_chapter,
            func.avg(RiskScore.score).label("avg_score"),
            func.count(TradeDeclaration.id).label("declaration_count"),
        )
        .join(RiskScore, RiskScore.declaration_id == TradeDeclaration.id)
        .group_by(TradeDeclaration.origin_country, hs_chapter)
        .order_by(func.avg(RiskScore.score).desc())
    )

    if date_from:
        query = query.where(TradeDeclaration.declaration_date >= date_from)
    if date_to:
        query = query.where(TradeDeclaration.declaration_date <= date_to)

    result = await db.execute(query)
    rows = result.all()

    return RiskHeatmapResponse(
        cells=[
            HeatmapCell(
                origin_country=row.origin_country,
                hs_chapter=row.hs_chapter,
                avg_score=round(float(row.avg_score), 2),
                declaration_count=row.declaration_count,
            )
            for row in rows
        ]
    )


@router.get("/distribution", response_model=RiskDistributionResponse)
async def risk_distribution(
    date_from: date | None = None,
    date_to: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Return the distribution of risk scores in predefined buckets
    (0-20, 20-40, 40-60, 60-80, 80-100). Useful for histogram charts.
    """
    buckets = [
        ("0-20", 0, 20),
        ("20-40", 20, 40),
        ("40-60", 40, 60),
        ("60-80", 60, 80),
        ("80-100", 80, 100),
    ]

    results = []
    for label, low, high in buckets:
        query = select(func.count(RiskScore.id)).where(
            RiskScore.score >= low, RiskScore.score < high
        )

        if date_from:
            query = query.join(TradeDeclaration).where(
                TradeDeclaration.declaration_date >= date_from
            )
        if date_to:
            if date_from is None:
                query = query.join(TradeDeclaration)
            query = query.where(TradeDeclaration.declaration_date <= date_to)

        count = (await db.execute(query)).scalar_one()
        results.append(RiskDistributionBucket(bucket=label, count=count))

    return RiskDistributionResponse(buckets=results)
