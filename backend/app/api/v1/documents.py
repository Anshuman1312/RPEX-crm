import uuid

from fastapi import APIRouter, Depends, Query
from fastapi import File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cloudinary import signed_delivery_url, upload_bytes
from app.core.config import get_settings
from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.audit_repository import AuditRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentAssetCreate
from app.services.document_service import DocumentService

router = APIRouter()
settings = get_settings()


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_DOCUMENTS}))])
async def create_document(payload: DocumentAssetCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = DocumentService(DocumentRepository(db), AuditRepository(db))
    row = await service.create_document(
        {
            **payload.model_dump(),
            "uploaded_by": current_user.id,
        },
        str(current_user.id),
    )
    return {
        "id": str(row.id),
        "category": row.category,
        "file_name": row.file_name,
        "storage_key": row.storage_key,
    }


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_DOCUMENTS}))])
async def list_documents(
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
    customer_id: str | None = Query(default=None),
    booking_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
):
    rows = await DocumentRepository(db).list_documents(customer_id=customer_id, booking_id=booking_id, limit=limit)
    return [
        {
            "id": str(row.id),
            "customer_id": str(row.customer_id) if row.customer_id else None,
            "booking_id": str(row.booking_id) if row.booking_id else None,
            "category": row.category,
            "file_name": row.file_name,
            "storage_key": row.storage_key,
            "content_type": row.content_type,
            "size_bytes": row.size_bytes,
            "partner_user_id": str(row.partner_user_id) if row.partner_user_id else None,
            "signed_url": signed_delivery_url(
                row.storage_key,
                (row.file_metadata or {}).get("resource_type", "image"),
            )
            if settings.cloudinary_cloud_name
            else (row.file_metadata or {}).get("cloudinary_url"),
        }
        for row in rows
    ]


@router.get("/{document_id}/signed-url", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_DOCUMENTS}))])
async def get_signed_document_url(document_id: str, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    row = await DocumentRepository(db).get_by_id(document_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    resource_type = (row.file_metadata or {}).get("resource_type", "image")
    if settings.cloudinary_cloud_name:
        url = signed_delivery_url(row.storage_key, resource_type)
    else:
        url = (row.file_metadata or {}).get("cloudinary_url")

    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signed URL unavailable")

    return {"id": str(row.id), "signed_url": url}


@router.post("/upload", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_DOCUMENTS}))])
async def upload_document(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    category: str = Query(..., min_length=2, max_length=64),
    customer_id: str | None = Query(default=None),
    booking_id: str | None = Query(default=None),
    partner_user_id: str | None = Query(default=None),
):
    if not settings.cloudinary_cloud_name or not settings.cloudinary_api_key or not settings.cloudinary_api_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloudinary is not configured",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")

    public_id = str(uuid.uuid4())
    upload_result = upload_bytes(
        file_bytes=file_bytes,
        public_id=public_id,
        folder=settings.cloudinary_folder,
    )

    storage_key = upload_result.get("public_id")
    secure_url = upload_result.get("secure_url")
    if not storage_key:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Cloudinary upload failed")

    service = DocumentService(DocumentRepository(db), AuditRepository(db))
    row = await service.create_document(
        {
            "customer_id": customer_id,
            "booking_id": booking_id,
            "category": category,
            "file_name": file.filename,
            "storage_key": storage_key,
            "content_type": file.content_type,
            "size_bytes": len(file_bytes),
            "partner_user_id": partner_user_id,
            "file_metadata": {
                "cloudinary_url": secure_url,
                "resource_type": upload_result.get("resource_type"),
                "format": upload_result.get("format"),
            },
            "uploaded_by": current_user.id,
        },
        str(current_user.id),
    )

    return {
        "id": str(row.id),
        "file_name": row.file_name,
        "category": row.category,
        "storage_key": row.storage_key,
        "url": secure_url,
    }