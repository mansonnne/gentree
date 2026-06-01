from uuid import UUID

from fastapi import APIRouter, Depends, Form, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.enums import DocumentKind
from app.modules.auth.dependencies import get_current_user
from app.modules.documents.schemas import DocumentRead
from app.modules.documents.service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    document_kind: DocumentKind = Form(DocumentKind.ATTACHMENT),
    archive_request_id: UUID | None = Form(None),
    person_id: UUID | None = Form(None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentRead:
    doc = await DocumentService(db).upload(
        file=file,
        document_kind=document_kind,
        user=current_user,
        archive_request_id=archive_request_id,
        person_id=person_id,
    )
    return DocumentRead.model_validate(doc)


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentRead:
    doc = await DocumentService(db).get_by_id(document_id, current_user)
    return DocumentRead.model_validate(doc)


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> FileResponse:
    svc = DocumentService(db)
    doc = await svc.get_by_id(document_id, current_user)
    path = svc.get_file_path(doc)
    return FileResponse(path=path, filename=doc.file_name, media_type=doc.mime_type)


@router.get("/by-archive-request/{archive_request_id}", response_model=list[DocumentRead])
async def docs_by_archive_request(
    archive_request_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[DocumentRead]:
    docs = await DocumentService(db).get_by_archive_request(archive_request_id, current_user)
    return [DocumentRead.model_validate(d) for d in docs]


@router.get("/by-person/{person_id}", response_model=list[DocumentRead])
async def docs_by_person(
    person_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[DocumentRead]:
    docs = await DocumentService(db).get_by_person(person_id, current_user)
    return [DocumentRead.model_validate(d) for d in docs]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    await DocumentService(db).delete(document_id, current_user)
