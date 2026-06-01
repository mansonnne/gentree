from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# psycopg3 (psycopg[binary]) supports async natively via postgresql+psycopg://
# No need to convert to asyncpg — avoids SSL negotiation issues with local PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
