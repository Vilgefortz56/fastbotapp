from contextlib import asynccontextmanager
import logging

from fastapi import  FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

from .config import Settings
from .db import close_db, async_session, init_db

from .storage import Dbstorage
from .models import User
from .middleware import WebhookMiddleware


logger = logging.getLogger(__name__)


class BotApp(FastAPI):
    def __init__(
        self, 
        settings: Settings,
        user_class: type[User] = None,
        allowed_updates: list[str] | None = None, 
        fsm_storage: Dbstorage = Dbstorage(),
        telegram_webhook_path: str = "/telegram/webhook",
        **kwargs
    ):
        if user_class is None:
            from .models.default_user import DefaultUser
            user_class = DefaultUser

        self.user_class = user_class
        self.settings = settings
        self.telegram_webhook_path = telegram_webhook_path
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher(storage=fsm_storage)
        self.allowed_updates = allowed_updates or ["message", "callback_query"]

        self.dp.update.middleware(WebhookMiddleware(self, async_session))

        super().__init__(lifespan=self.default_lifespan, **kwargs)

        self.add_api_route(path=self.telegram_webhook_path , endpoint=self._webhook_handler, methods=["POST"])

    @asynccontextmanager
    async def default_lifespan(self, app: FastAPI):
        logger.info("Запуск приложения BotApp")
        await init_db()
        await self.set_webhook()
        yield
        logger.info("Остановка приложения BotApp")
        await self.bot.delete_webhook()
        await self.bot.session.close()
        await close_db()

    async def set_webhook(self):
        await self.bot.set_webhook(
            url=f"{self.settings.TELEGRAM_WEBHOOK_URL}{self.telegram_webhook_path}",
            drop_pending_updates=True,
            allowed_updates=self.allowed_updates,
            secret_token=self.settings.TELEGRAM_WEBHOOK_AUTH_KEY,
        )


    async def _webhook_handler(self, request: Request):
        try:
            # Логируем входящий запрос
            request_data = await request.json()
            logging.debug(f"Webhook request: {request_data}")
            
            # Проверяем секретный токен
            request_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if request_token != self.settings.TELEGRAM_WEBHOOK_AUTH_KEY:
                logging.warning(f"Unauthorized webhook request from {request.client.host}")
                return Response(status_code=403)

            try:
                update = Update(**request_data)
                await self.dp.feed_webhook_update(self.bot, update)
                return Response(status_code=200)
            except Exception as e:
                logging.error(f"Invalid update format: {e}")
                return Response(status_code=400)
            
        
        except Exception as e:
            logging.error(f"Ошибка при обработке webhook: {e}")
            return Response(status_code=400)
    
   

    # async def get_user(self, user_id: int) -> Optional[User]:
    #     """Получение пользователя из базы данных"""
    #     async with get_db() as session:
    #         return await User.get_by_id(session, user_id)
    
    # async def create_or_update_user(self, user_data: dict) -> User:
    #     """Создание или обновление пользователя"""
    #     async with get_db() as session:
    #         return await User.create_or_update(session, user_data)
