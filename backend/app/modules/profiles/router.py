from fastapi import APIRouter

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/ping")
async def profiles_ping() -> dict[str, str]:
    return {"module": "profiles", "status": "ready"}

