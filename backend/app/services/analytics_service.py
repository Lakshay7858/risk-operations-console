"""
Business logic layer for analytics computations.

Provides cacheable, testable functions that the API layer delegates to.
Keeps route handlers thin and focused on HTTP concerns.
"""

from datetime import date, timedelta
from uuid import UUID

import redis.asyncio as aioredis
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.trade import TradeDeclaration, RiskScore, Importer

settings = get_settings()


async def get_redis() -> aioredis.Redis:
    """Create and return an async Redis client."""
    return aioredis.from_url(settings.redis_url, decode_responses=True)


async def compute_moving_average(
    db: AsyncSession,
    window_days: int = 30,
    end_date: date | None = None,
    hs_code_prefix: str | None = None,
) -> list[dict]:
    """
    Compute a rolling moving average of daily trade values over the given window.

    Returns a list of dicts with keys: date, moving_avg_value, daily_count.
    """
    if end_date is None:
        end_date = date.today()

    start_date = end_date - timedelta(days=window_days * 2)

    query = (
        select(
            TradeDeclaration.declaration_date,
            func.count(TradeDeclaration.id).label("daily_count"),
            func.sum(TradeDeclaration.declared_value).label("daily_value"),
        )
        .where(TradeDeclaration.declaration_date.between(start_date, end_date))
        .group_by(TradeDeclaration.declaration_date)
        .order_by(TradeDeclaration.declaration_date)
    )

    if hs_code_prefix:
        query = query.where(TradeDeclaration.hs_code.startswith(hs_code_prefix))

    result = await db.execute(query)
    rows = result.all()

    daily_values = [(row.declaration_date, float(row.daily_value or 0), row.daily_count) for row in rows]

    moving_averages = []
    for i in range(len(daily_values)):
        window_start = max(0, i - window_days + 1)
        window = daily_values[window_start : i + 1]
        avg_val = sum(v[1] for v in window) / len(window) if window else 0
        moving_averages.append(
            {
                "date": daily_values[i][0].isoformat(),
                "moving_avg_value": round(avg_val, 2),
                "daily_count": daily_values[i][2],
            }
        )

    return moving_averages


async def compute_risk_percentiles(
    db: AsyncSession,
    percentiles: list[float] | None = None,
) -> dict[str, float]:
    """
    Compute percentile values for risk scores across all declarations.

    Returns a mapping of percentile label to score value,
    e.g. {"p50": 42.5, "p90": 78.3, "p95": 88.1, "p99": 96.2}.
    """
    if percentiles is None:
        percentiles = [0.50, 0.90, 0.95, 0.99]

    result = await db.execute(select(RiskScore.score).order_by(RiskScore.score))
    scores = [row[0] for row in result.all()]

    if not scores:
        return {f"p{int(p * 100)}": 0.0 for p in percentiles}

    output = {}
    n = len(scores)
    for p in percentiles:
        idx = int(p * (n - 1))
        output[f"p{int(p * 100)}"] = round(scores[idx], 2)

    return output


async def identify_value_outliers(
    db: AsyncSession,
    hs_code_prefix: str,
    std_dev_threshold: float = 2.0,
) -> list[dict]:
    """
    Identify trade declarations whose declared value deviates significantly
    from the mean for a given HS code prefix.

    Returns declarations that exceed mean +/- (std_dev_threshold * std_dev).
    """
    stats_query = select(
        func.avg(TradeDeclaration.declared_value).label("mean_value"),
        func.stddev(TradeDeclaration.declared_value).label("std_value"),
    ).where(TradeDeclaration.hs_code.startswith(hs_code_prefix))

    stats_result = await db.execute(stats_query)
    stats = stats_result.one()

    if stats.mean_value is None or stats.std_value is None or float(stats.std_value) == 0:
        return []

    mean_val = float(stats.mean_value)
    std_val = float(stats.std_value)
    lower_bound = mean_val - std_dev_threshold * std_val
    upper_bound = mean_val + std_dev_threshold * std_val

    outlier_query = (
        select(TradeDeclaration)
        .where(TradeDeclaration.hs_code.startswith(hs_code_prefix))
        .where(
            (TradeDeclaration.declared_value < lower_bound)
            | (TradeDeclaration.declared_value > upper_bound)
        )
        .order_by(TradeDeclaration.declared_value.desc())
        .limit(100)
    )

    result = await db.execute(outlier_query)
    outliers = result.scalars().all()

    return [
        {
            "declaration_id": str(o.id),
            "declaration_number": o.declaration_number,
            "declared_value": float(o.declared_value),
            "deviation": round(
                (float(o.declared_value) - mean_val) / std_val, 2
            ),
            "hs_code": o.hs_code,
            "origin_country": o.origin_country,
        }
        for o in outliers
    ]


async def get_corridor_summary(
    db: AsyncSession,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[dict]:
    """
    Summarize trade corridors (origin -> destination pairs) with volume,
    value, and risk metrics. Useful for identifying high-risk trade routes.
    """
    avg_risk = (
        select(func.avg(RiskScore.score))
        .where(RiskScore.declaration_id == TradeDeclaration.id)
        .correlate(TradeDeclaration)
        .scalar_subquery()
    )

    query = (
        select(
            TradeDeclaration.origin_country,
            TradeDeclaration.destination_country,
            func.count(TradeDeclaration.id).label("declaration_count"),
            func.sum(TradeDeclaration.declared_value).label("total_value"),
            func.sum(TradeDeclaration.weight_kg).label("total_weight"),
            func.avg(avg_risk).label("avg_risk_score"),
            func.sum(
                func.cast(TradeDeclaration.is_flagged, type_=func.integer if hasattr(func, 'integer') else None)
            ).label("flagged_count"),
        )
        .group_by(
            TradeDeclaration.origin_country,
            TradeDeclaration.destination_country,
        )
        .order_by(func.sum(TradeDeclaration.declared_value).desc())
    )

    if date_from:
        query = query.where(TradeDeclaration.declaration_date >= date_from)
    if date_to:
        query = query.where(TradeDeclaration.declaration_date <= date_to)

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "origin": row.origin_country,
            "destination": row.destination_country,
            "declaration_count": row.declaration_count,
            "total_value": float(row.total_value or 0),
            "total_weight": float(row.total_weight or 0),
            "avg_risk_score": round(float(row.avg_risk_score), 2)
            if row.avg_risk_score
            else None,
        }
        for row in rows
    ]
