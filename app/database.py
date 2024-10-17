import logging
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import Column, Integer, func
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker,
)
from sqlalchemy.orm import (
    declarative_base, declared_attr, Mapped, mapped_column,
)

from app.config import settings

logger = logging.getLogger(__name__)


class PreBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return self.__tablename__


Base = declarative_base(cls=PreBase)

engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        try:
            yield async_session
        except HTTPException as e:
            logger.exception('HTTPException %s', e)
            raise e
