from fastapi import APIRouter

router = APIRouter(prefix="/archive-requests", tags=["archive_requests"])


@router.get("/ping")
async def archive_requests_ping() -> dict[str, str]:
    return {"module": "archive_requests", "status": "ready"}

