from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/ping")
async def notifications_ping() -> dict[str, str]:
    return {"module": "notifications", "status": "ready"}

