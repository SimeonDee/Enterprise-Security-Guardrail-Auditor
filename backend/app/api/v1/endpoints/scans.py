from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.models.scan import Scan
from app.schemas.scan import ScanCreate, ScanDetailResponse, ScanResponse
from app.services.scanner import ScannerService

router = APIRouter()


@router.get("/", response_model=list[ScanResponse])
async def list_scans(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[Scan]:
    stmt = select(Scan).order_by(Scan.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post(
    "/", response_model=ScanDetailResponse, status_code=status.HTTP_201_CREATED
)
async def create_scan(payload: ScanCreate, db: AsyncSession = Depends(get_db)) -> Scan:
    service = ScannerService(db)
    scan = await service.run_scan(payload)
    return scan


@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(scan_id: int, db: AsyncSession = Depends(get_db)) -> Scan:
    stmt = select(Scan).where(Scan.id == scan_id).options(selectinload(Scan.violations))
    result = await db.execute(stmt)
    scan = result.scalars().first()
    if not scan:
        raise NotFoundError("Scan", scan_id)
    return scan


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(scan_id: int, db: AsyncSession = Depends(get_db)) -> None:
    stmt = select(Scan).where(Scan.id == scan_id)
    result = await db.execute(stmt)
    scan = result.scalars().first()
    if not scan:
        raise NotFoundError("Scan", scan_id)
    await db.delete(scan)
    await db.commit()
