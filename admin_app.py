"""ADMIN APP"""
from aiogram import executor
from admin_loader import bot, pay_bot, dp, storage
import utils.admin.handlers
from utils.admin.main import main
from utils.admin.notify_admins import (on_startup_notify,
                                       on_shutdown_notify)


async def on_startup(dp):
    await on_startup_notify(bot)
    await main(dp, bot)
    # filters.setup(dp)
    # middlewares.setup(dp)


async def on_shutdown(dp):
    await on_shutdown_notify(bot)
    await bot.close()
    await pay_bot.close()
    await storage.close()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
