from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.profiles.schemas import ProfileCreate, ProfileRead, ProfileUpdate
from app.modules.profiles.service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: ProfileCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ProfileRead:
    profile = await ProfileService(db).create(data, current_user)
    return ProfileRead.model_validate(profile)


@router.get("/my", response_model=list[ProfileRead])
async def my_profiles(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[ProfileRead]:
    profiles = await ProfileService(db).get_my(current_user)
    return [ProfileRead.model_validate(p) for p in profiles]


@router.get("/{profile_id}", response_model=ProfileRead)
async def get_profile(
    profile_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ProfileRead:
    profile = await ProfileService(db).get_by_id(profile_id, current_user)
    return ProfileRead.model_validate(profile)


@router.patch("/{profile_id}", response_model=ProfileRead)
async def update_profile(
    profile_id: UUID,
    data: ProfileUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ProfileRead:
    profile = await ProfileService(db).update(profile_id, data, current_user)
    return ProfileRead.model_validate(profile)
