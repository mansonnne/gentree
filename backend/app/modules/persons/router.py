from fastapi import APIRouter

router = APIRouter(prefix="/persons", tags=["persons"])


@router.get("/ping")
async def persons_ping() -> dict[str, str]:
    return {"module": "persons", "status": "ready"}

