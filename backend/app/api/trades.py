from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import get_db
from app.models.trade import TradeDeclaration, Importer
from app.schemas.trade import (
    TradeDeclarationCreate,
    TradeDeclarationRead,
    TradeDeclarationDetail,
    PaginatedResponse,
)

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_declarations(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    direction: str | None = Query(None, pattern="^(import|export)$"),
    db: AsyncSession = Depends(get_db),
):
    """List trade declarations with pagination and optional direction filter."""
    query = select(TradeDeclaration)

    if direction:
        query = query.where(TradeDeclaration.direction == direction)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(TradeDeclaration.declaration_date.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[TradeDeclarationRead.model_validate(item) for item in items],
    )


@router.get("/search", response_model=PaginatedResponse)
async def search_declarations(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    hs_code: str | None = None,
    origin_country: str | None = None,
    destination_country: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
    flagged_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Search and filter trade declarations across multiple dimensions."""
    query = select(TradeDeclaration)

    if hs_code:
        query = query.where(TradeDeclaration.hs_code.startswith(hs_code))
    if origin_country:
        query = query.where(TradeDeclaration.origin_country == origin_country.upper())
    if destination_country:
        query = query.where(
            TradeDeclaration.destination_country == destination_country.upper()
        )
    if date_from:
        query = query.where(TradeDeclaration.declaration_date >= date_from)
    if date_to:
        query = query.where(TradeDeclaration.declaration_date <= date_to)
    if min_value is not None:
        query = query.where(TradeDeclaration.declared_value >= min_value)
    if max_value is not None:
        query = query.where(TradeDeclaration.declared_value <= max_value)
    if flagged_only:
        query = query.where(TradeDeclaration.is_flagged.is_(True))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(TradeDeclaration.declaration_date.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[TradeDeclarationRead.model_validate(item) for item in items],
    )


@router.get("/{declaration_id}", response_model=TradeDeclarationDetail)
async def get_declaration(
    declaration_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a single trade declaration with its importer and risk scores."""
    result = await db.execute(
        select(TradeDeclaration).where(TradeDeclaration.id == declaration_id)
    )
    declaration = result.scalar_one_or_none()

    if not declaration:
        raise HTTPException(status_code=404, detail="Declaration not found")

    return TradeDeclarationDetail.model_validate(declaration)


@router.post("", response_model=TradeDeclarationRead, status_code=201)
async def create_declaration(
    payload: TradeDeclarationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new trade declaration."""
    importer = await db.get(Importer, payload.importer_id)
    if not importer:
        raise HTTPException(status_code=404, detail="Importer not found")

    declaration = TradeDeclaration(**payload.model_dump())
    db.add(declaration)
    await db.commit()
    await db.refresh(declaration)

    return TradeDeclarationRead.model_validate(declaration)
