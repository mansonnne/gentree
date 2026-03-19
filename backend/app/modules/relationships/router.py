from fastapi import APIRouter

router = APIRouter(prefix="/relationships", tags=["relationships"])


@router.get("/ping")
async def relationships_ping() -> dict[str, str]:
    return {"module": "relationships", "status": "ready"}

