from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.enums import UserRole, UserStatus
from app.models.user import User
from app.modules.auth.schemas import LoginRequest, RegisterRequest
from app.repositories.user import UserRepository


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def register(self, data: RegisterRequest) -> User:
        if await self.repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        return await self.repo.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            first_name=data.first_name,
            last_name=data.last_name,
            middle_name=data.middle_name,
        )

    async def login(self, data: LoginRequest) -> str:
        user = await self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if user.status == UserStatus.BLOCKED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is blocked",
            )
        return create_access_token(user.id, user.role)
