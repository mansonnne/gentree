from fastapi import APIRouter

router = APIRouter(prefix="/facts", tags=["facts"])


@router.get("/ping")
async def facts_ping() -> dict[str, str]:
    return {"module": "facts", "status": "ready"}

