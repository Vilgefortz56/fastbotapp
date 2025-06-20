from typing import Optional, Dict, Any
from datetime import datetime, timezone

from .role import UserRole

from sqlmodel import SQLModel, Field, select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.storage.base import StorageKey


class BaseModel(SQLModel):
    """Базовая модель с общими полями"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class User(BaseModel, table=True):
    """Модель пользователя"""    
    telegram_id: int = Field(unique=True, index=True)
    username: Optional[str] = None
    role: str = Field(default=UserRole.USER.value, index=True)

    def is_admin(self) -> bool:
        """Проверить, является ли пользователь администратором"""
        return self.role in [UserRole.ADMIN.value]
    
    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: int) -> Optional["User"]:
        """Получение пользователя по ID"""
        stmt = select(cls).where(cls.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @classmethod
    async def create_or_update(cls, session: AsyncSession, user_data: dict) -> "User":
        """Создание или обновление пользователя"""
        user = await cls.get_by_id(session, user_data["id"])
        
        if user:
            # Обновление существующего пользователя
            for key, value in user_data.items():
                if key == "id":
                    continue
                setattr(user, key.replace("id", "user_id") if key == "id" else key, value)
            user.updated_at = datetime.now(datetime.timezone.utc)
        else:
            # Создание нового пользователя
            user_data["user_id"] = user_data.pop("id")
            user = cls(**user_data)
            session.add(user)
        
        await session.commit()
        await session.refresh(user)
        return user