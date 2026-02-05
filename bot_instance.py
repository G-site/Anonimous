from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import os


TOKEN = os.environ.get("TOKEN")


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher()
