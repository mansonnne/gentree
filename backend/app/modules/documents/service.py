from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import delete_file, save_upload
from app.models.document import Document
from app.models.enums import DocumentKind, DocumentSourceType, UserRole
from app.models.user import User
from app.repositories.document import DocumentRepository


class DocumentService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = DocumentRepository(db)

    async def upload(
        self,
        file: UploadFile,
        document_kind: DocumentKind,
        user: User,
        archive_request_id: UUID | None = None,
        person_id: UUID | None = None,
    ) -> Document:
        storage_path, sha256, size = await save_upload(file)

        doc = await self.repo.create(
            uploaded_by_user_id=user.id,
            document_kind=document_kind,
            source_type=DocumentSourceType.USER_UPLOAD,
            file_name=file.filename or Path(storage_path).name,
            mime_type=file.content_type or "application/octet-stream",
            file_size_bytes=size,
            storage_path=storage_path,
            checksum_sha256=sha256,
        )

        if archive_request_id:
            await self.repo.link_to_archive_request(doc.id, archive_request_id)
        if person_id:
            await self.repo.link_to_person(doc.id, person_id)

        return await self.repo.commit_and_refresh(doc)

    async def get_by_id(self, document_id: UUID, user: User) -> Document:
        doc = await self.repo.get_by_id(document_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if user.role != UserRole.ADMIN and doc.uploaded_by_user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return doc

    async def get_by_archive_request(
        self, archive_request_id: UUID, user: User
    ) -> list[Document]:
        return await self.repo.get_by_archive_request(archive_request_id)

    async def get_by_person(self, person_id: UUID, user: User) -> list[Document]:
        return await self.repo.get_by_person(person_id)

    async def delete(self, document_id: UUID, user: User) -> None:
        doc = await self.get_by_id(document_id, user)
        delete_file(doc.storage_path)
        await self.repo.delete(doc)

    def get_file_path(self, doc: Document) -> str:
        if not Path(doc.storage_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk"
            )
        return doc.storage_path
