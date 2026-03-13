import asyncio
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo
from bot_instance import bot


CHAT_ID = -1003219172904
PHOTO_PATH = "https://i.postimg.cc/3RtF5xQy/photo-2026-03-13-16-50-35.jpg"


async def weekly_message():
    await bot.send_photo(
        chat_id=CHAT_ID,
        photo=PHOTO_PATH,
        caption="🕵️‍♂️Бот работает в штатном режиме! -> @Anonim_messssage_bot"
    )


def setup_scheduler():
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))

    scheduler.add_job(
        weekly_message,
        CronTrigger(
            day_of_week="sun",
            hour=14,
            minute=0
        )
    )
    scheduler.start()
