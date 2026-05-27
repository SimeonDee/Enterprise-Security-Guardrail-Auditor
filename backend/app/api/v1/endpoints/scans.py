from fastapi import APIRouter, Depends, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import ValidationError
from app.database import get_db
from app.models.scan import FileType, ScanStatus
from app.schemas.scan import (
    PaginatedResponse,
    ScanCreate,
    ScanDetailResponse,
    ScanResponse,
)
from app.services.scanner import ScannerService

router = APIRouter()
settings = get_settings()


def _get_service(db: AsyncSession = Depends(get_db)) -> ScannerService:
    return ScannerService(db)


@router.get("/", response_model=PaginatedResponse[ScanResponse])
async def list_scans(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: ScanStatus | None = Query(None, description="Filter by scan status"),
    file_type: FileType | None = Query(None, description="Filter by file type"),
    service: ScannerService = Depends(_get_service),
) -> PaginatedResponse[ScanResponse]:
    return await service.list_scans(
        page=page, page_size=page_size, status=status, file_type=file_type
    )


@router.post(
    "/", response_model=ScanDetailResponse, status_code=status.HTTP_201_CREATED
)
async def create_scan(
    payload: ScanCreate,
    service: ScannerService = Depends(_get_service),
) -> ScanDetailResponse:
    scan = await service.run_scan(payload)
    return ScanDetailResponse.model_validate(scan)


@router.post(
    "/upload",
    response_model=ScanDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_scan(
    file: UploadFile,
    name: str = Query(..., min_length=1, max_length=255, description="Scan name"),
    service: ScannerService = Depends(_get_service),
) -> ScanDetailResponse:
    """Upload a .tf file and run a security scan against it."""
    if not file.filename:
        raise ValidationError("Uploaded file must have a filename.")
    if not file.filename.endswith(".tf"):
        raise ValidationError("Only Terraform (.tf) files are supported.")

    content_bytes = await file.read()
    if not content_bytes:
        raise ValidationError("Uploaded file is empty.")

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content_bytes) > max_bytes:
        raise ValidationError(f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit.")

    try:
        source_content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise ValidationError("File is not valid UTF-8 text.") from None

    payload = ScanCreate(
        name=name,
        file_type=FileType.TERRAFORM,
        source_content=source_content,
        file_name=file.filename,
    )
    scan = await service.run_scan(payload)
    return ScanDetailResponse.model_validate(scan)


@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(
    scan_id: int,
    service: ScannerService = Depends(_get_service),
) -> ScanDetailResponse:
    scan = await service.get_scan(scan_id)
    return ScanDetailResponse.model_validate(scan)


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: int,
    service: ScannerService = Depends(_get_service),
) -> None:
    await service.delete_scan(scan_id)
