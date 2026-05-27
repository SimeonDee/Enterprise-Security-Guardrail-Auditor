from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.database import get_db
from app.models.guardrail import Guardrail
from app.schemas.guardrail import GuardrailCreate, GuardrailResponse, GuardrailUpdate

router = APIRouter()


@router.get("/", response_model=list[GuardrailResponse])
async def list_guardrails(
    skip: int = 0,
    limit: int = Query(100, ge=1, le=500),
    enabled: bool | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[Guardrail]:
    stmt = select(Guardrail)
    if enabled is not None:
        stmt = stmt.where(Guardrail.enabled == enabled)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/", response_model=GuardrailResponse, status_code=status.HTTP_201_CREATED)
async def create_guardrail(
    payload: GuardrailCreate, db: AsyncSession = Depends(get_db)
) -> Guardrail:
    stmt = select(Guardrail).where(Guardrail.name == payload.name)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise ConflictError("Guardrail", "name", payload.name)
    guardrail = Guardrail(**payload.model_dump())
    db.add(guardrail)
    await db.commit()
    await db.refresh(guardrail)
    return guardrail


@router.get("/{guardrail_id}", response_model=GuardrailResponse)
async def get_guardrail(
    guardrail_id: int, db: AsyncSession = Depends(get_db)
) -> Guardrail:
    stmt = select(Guardrail).where(Guardrail.id == guardrail_id)
    result = await db.execute(stmt)
    guardrail = result.scalars().first()
    if not guardrail:
        raise NotFoundError("Guardrail", guardrail_id)
    return guardrail


@router.patch("/{guardrail_id}", response_model=GuardrailResponse)
async def update_guardrail(
    guardrail_id: int,
    payload: GuardrailUpdate,
    db: AsyncSession = Depends(get_db),
) -> Guardrail:
    stmt = select(Guardrail).where(Guardrail.id == guardrail_id)
    result = await db.execute(stmt)
    guardrail = result.scalars().first()
    if not guardrail:
        raise NotFoundError("Guardrail", guardrail_id)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(guardrail, field, value)
    await db.commit()
    await db.refresh(guardrail)
    return guardrail


@router.delete("/{guardrail_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_guardrail(
    guardrail_id: int, db: AsyncSession = Depends(get_db)
) -> None:
    stmt = select(Guardrail).where(Guardrail.id == guardrail_id)
    result = await db.execute(stmt)
    guardrail = result.scalars().first()
    if not guardrail:
        raise NotFoundError("Guardrail", guardrail_id)
    await db.delete(guardrail)
    await db.commit()
