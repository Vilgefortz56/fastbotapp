from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from ..db import async_session

class WebhookMiddleware(BaseMiddleware):
    """Middleware для передачи данных из FastAPI в aiogram"""
    
    def __init__(self, app, db_session: AsyncSession):
        self.app = app
        self.db_session = db_session
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Добавляем данные в контекст
        data["app"] = self.app
        # data["db_session"] = self.db_session
        async with async_session() as session:
            data['db_session'] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
        
        
        return await handler(event, data)