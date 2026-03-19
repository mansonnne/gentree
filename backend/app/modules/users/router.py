from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/ping")
async def users_ping() -> dict[str, str]:
    return {"module": "users", "status": "ready"}

