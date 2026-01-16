from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import DATABASE_URL

# Engine — один на приложение
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


# Dependency / helper
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
