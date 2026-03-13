import asyncio
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


from apps.handlers import router
from apps.message import message_router
from apps.admin import admin_router
from apps.database import connect
from bot_instance import bot, dp
from apps.sender import setup_scheduler


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="📋 Меню"),
        BotCommand(command="profile", description="👤 Профиль"),
        BotCommand(command="send", description="💌 Отправить сообщение"),
        BotCommand(command="about", description="ℹ️ О нас"),
        BotCommand(command="instruction", description="❓ FAQ")
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def main():
    setup_scheduler()
    await connect()
    await set_bot_commands(bot)
    dp.include_router(router)
    dp.include_router(admin_router)
    dp.include_router(message_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
