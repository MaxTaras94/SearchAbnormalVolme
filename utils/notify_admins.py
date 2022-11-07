# import logging
from aiogram import Bot
from data.config import ADMINS


async def on_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(admin, "Бот поднялся")
        except Exception as err:
            # logging.exception(err)
            print(err)


async def on_shutdown_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(admin, "Бот упал")
        except Exception as err:
            # logging.exception(err)
            print(err)
