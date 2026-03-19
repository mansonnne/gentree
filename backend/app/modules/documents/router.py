from fastapi import APIRouter

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/ping")
async def documents_ping() -> dict[str, str]:
    return {"module": "documents", "status": "ready"}

