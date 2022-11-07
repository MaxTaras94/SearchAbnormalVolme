import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.config import TOKEN
# from utils.db_api.database import db_create_pool


loop = asyncio.get_event_loop()

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# db = loop.run_until_complete(db_create_pool())
