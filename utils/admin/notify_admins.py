import logging
from aiogram import Dispatcher, Bot
from data.config import ADMINS


async def on_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(admin, "Admin Bot Встал")
        except Exception as err:
            logging.exception(err)


async def on_shutdown_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(admin, "Admin Bot Лёг")
        except Exception as err:
            logging.exception(err)


async def app_notify(bot: Bot, text: str):
    for admin in ADMINS:
        try:
            await bot.send_message(admin, text)
        except Exception as err:
            logging.exception(err)
