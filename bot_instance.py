from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os


load_dotenv()
TOKEN = os.environ.get("TOKEN")


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher()
