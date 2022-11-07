"""ADMIN LOADER"""
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.config import (ADMIN_BOT_TRADERHELPER_TOKEN,
                         PAY_BOT_TRADERHELPER_TOKEN)


loop = asyncio.get_event_loop()

bot = Bot(token=ADMIN_BOT_TRADERHELPER_TOKEN,
          parse_mode=types.ParseMode.HTML)
pay_bot = Bot(token=PAY_BOT_TRADERHELPER_TOKEN,
              parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
