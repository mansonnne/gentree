import hashlib
import os
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


def _upload_dir() -> Path:
    path = Path(settings.upload_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


async def save_upload(file: UploadFile) -> tuple[str, str, int]:
    """Save uploaded file to disk. Returns (storage_path, sha256_hex, size_bytes)."""
    upload_dir = _upload_dir()
    ext = Path(file.filename or "").suffix.lower()
    dest = upload_dir / f"{uuid4()}{ext}"

    sha256 = hashlib.sha256()
    total = 0
    with open(dest, "wb") as f:
        while chunk := await file.read(65536):
            f.write(chunk)
            sha256.update(chunk)
            total += len(chunk)

    return str(dest), sha256.hexdigest(), total


def delete_file(storage_path: str) -> None:
    try:
        os.remove(storage_path)
    except FileNotFoundError:
        pass
