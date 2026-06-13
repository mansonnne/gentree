import hashlib
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.book import GeneratedBook
from app.models.document import Document
from app.models.enums import BookStatus, DocumentKind, DocumentSourceType, UserRole
from app.models.user import User
from app.repositories.fact import FactRepository
from app.repositories.person import PersonRepository
from app.repositories.profile import ProfileRepository

_FACT_TYPE_RU = {
    "BIRTH": "Рождение", "DEATH": "Смерть", "MARRIAGE": "Брак",
    "RESIDENCE": "Проживание", "SERVICE": "Служба", "NOTE": "Заметка",
}
_CONF_RU = {
    "UNVERIFIED": "Не проверено", "HYPOTHESIS": "Гипотеза",
    "PROBABLE": "Вероятно", "CONFIRMED": "Подтверждено",
}
_SEX_RU = {"MALE": "Мужской", "FEMALE": "Женский", "UNKNOWN": "Неизвестно"}


def _build_html(profile, persons, facts_by_person: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
    parts = [
        '<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">',
        f'<title>Генеалогическая книга: {profile.title}</title>',
        "<style>",
        "body{font-family:Arial,sans-serif;margin:40px;color:#1f2937;line-height:1.5}",
        "h1{color:#4f46e5;margin-bottom:4px}h2{color:#374151;border-bottom:1px solid #e5e7eb;padding-bottom:4px;margin-top:32px}",
        "table{border-collapse:collapse;width:100%;margin:8px 0;font-size:14px}",
        "th,td{border:1px solid #e5e7eb;padding:6px 10px;text-align:left}th{background:#f9fafb}",
        ".meta{color:#6b7280;font-size:14px;margin:4px 0}.card{margin-bottom:28px}",
        "</style></head><body>",
        f"<h1>Генеалогическая книга</h1>",
        f"<h2 style='color:#4f46e5;border:none'>{profile.title}</h2>",
    ]
    if profile.description:
        parts.append(f"<p>{profile.description}</p>")
    parts.append(f"<p class='meta'>Сформировано: {now} · Персон: {len(persons)}</p><hr>")

    for person in persons:
        full_name = " ".join(x for x in [person.last_name, person.first_name, person.middle_name] if x)
        sex = _SEX_RU.get(str(person.sex), "?")
        parts.append(f"<div class='card'><h2>{full_name}</h2>")
        meta_items = [f"Пол: {sex}"]
        if person.birth_date:
            meta_items.append(f"Рождение: {person.birth_date}")
        if person.birth_place:
            meta_items.append(f"Место рождения: {person.birth_place}")
        if not person.is_living:
            if person.death_date:
                meta_items.append(f"Смерть: {person.death_date}")
            if person.death_place:
                meta_items.append(f"Место смерти: {person.death_place}")
        parts.append(f"<p class='meta'>{' · '.join(meta_items)}</p>")
        if person.notes:
            parts.append(f"<p><em>{person.notes}</em></p>")

        facts = facts_by_person.get(person.id, [])
        if facts:
            parts.append(
                "<table><thead><tr>"
                "<th>Тип</th><th>Дата</th><th>Место</th><th>Описание</th><th>Достоверность</th>"
                "</tr></thead><tbody>"
            )
            for f in facts:
                parts.append(
                    f"<tr><td>{_FACT_TYPE_RU.get(str(f.fact_type), str(f.fact_type))}</td>"
                    f"<td>{f.fact_date or '—'}</td><td>{f.place or '—'}</td>"
                    f"<td>{f.value_text or '—'}</td>"
                    f"<td>{_CONF_RU.get(str(f.confidence), str(f.confidence))}</td></tr>"
                )
            parts.append("</tbody></table>")
        parts.append("</div>")

    parts.append("</body></html>")
    return "\n".join(parts)


class BookService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.profile_repo = ProfileRepository(db)
        self.person_repo = PersonRepository(db)
        self.fact_repo = FactRepository(db)

    async def _get_profile_or_403(self, profile_id: UUID, user: User):
        profile = await self.profile_repo.get_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        if user.role != UserRole.ADMIN and profile.owner_user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return profile

    async def create_book(self, profile_id: UUID, user: User) -> GeneratedBook:
        profile = await self._get_profile_or_403(profile_id, user)

        book = GeneratedBook(
            profile_id=profile_id,
            requested_by_user_id=user.id,
            status=BookStatus.IN_PROGRESS,
        )
        self.db.add(book)
        await self.db.flush()

        try:
            persons = await self.person_repo.get_by_profile(profile_id)
            facts_by_person = {}
            for p in persons:
                facts_by_person[p.id] = await self.fact_repo.get_by_person(p.id)

            html = _build_html(profile, persons, facts_by_person)
            raw = html.encode("utf-8")

            upload_dir = Path(settings.upload_dir)
            upload_dir.mkdir(parents=True, exist_ok=True)
            dest = upload_dir / f"book_{book.id}.html"
            dest.write_bytes(raw)

            doc = Document(
                uploaded_by_user_id=user.id,
                document_kind=DocumentKind.BOOK_RESULT,
                source_type=DocumentSourceType.SYSTEM_GENERATED,
                file_name=f"{profile.title}_книга.html",
                mime_type="text/html; charset=utf-8",
                file_size_bytes=len(raw),
                storage_path=str(dest),
                checksum_sha256=hashlib.sha256(raw).hexdigest(),
            )
            self.db.add(doc)
            await self.db.flush()

            book.document_id = doc.id
            book.status = BookStatus.SUCCEEDED
            book.finished_at = datetime.now(timezone.utc)

        except Exception as exc:
            book.status = BookStatus.FAILED
            book.error_message = str(exc)
            book.finished_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def list_books(self, profile_id: UUID, user: User) -> list[GeneratedBook]:
        await self._get_profile_or_403(profile_id, user)
        result = await self.db.execute(
            select(GeneratedBook)
            .where(GeneratedBook.profile_id == profile_id)
            .order_by(GeneratedBook.created_at.desc())
        )
        return list(result.scalars().all())
