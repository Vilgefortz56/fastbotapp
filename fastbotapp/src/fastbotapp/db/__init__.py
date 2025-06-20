from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from ..config import settings

# from ..config import config

# import logging
# logger = logging.getLogger('sqlalchemy.engine')
# logger.setLevel(logging.DEBUG)

async_engine = create_async_engine(settings.DATABASE_URI)
async_session = sessionmaker[AsyncSession](
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncSession:  # type: ignore
    async with async_session() as session:
        yield session

async def init_db():
    """Инициализация базы данных"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def close_db():
    await async_engine.dispose()