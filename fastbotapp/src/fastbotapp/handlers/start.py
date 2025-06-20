from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from logging import getLogger
from sqlmodel.ext.asyncio.session import AsyncSession

from ..main import BotApp
from ..models.user import User, UserRole

logger = getLogger(__name__)
router = Router()

@router.message(CommandStart())
async def start(message: Message, **kwargs):
    app: BotApp = kwargs["app"]
    state: FSMContext = kwargs["state"]
    db_session: AsyncSession = kwargs["db_session"]

    tg_user = message.from_user
    settings = app.settings

    await state.clear()

    if settings.DB_CREATE_USER:
        user = await User.create_or_update(
            telegram_id = tg_user.id,
            username = tg_user.username,
            role = UserRole.ADMIN if tg_user.id in settings.TELEGRAM_ADMIN_ID else UserRole.USER
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)


