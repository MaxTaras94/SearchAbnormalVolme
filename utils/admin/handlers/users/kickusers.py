from admin_loader import dp, pay_bot
from aiogram import types
from aiogram.dispatcher.filters.builtin import Command
from aiogram.utils.markdown import hlink
from data.config import ADMINS
import datetime
from dateutil import relativedelta
import logging
from utils.db_api.db_commands import database


@dp.message_handler(Command("kickusers"), state="*")
async def bot_kickusers(message: types.Message = None):
    """
    /kickusers функция бота.
    """

    t1 = datetime.datetime.now()
    text = "Start <b>kickChatMember</b> method\n"
    if message is not None:
        await message.answer(text=text)

    data = await database.get_users_active_subscribes()
    time = datetime.datetime.now()
    N = 0
    for row in data:
        if row["paid_till"] < time:
            channel_id = int(row["subscribe_channel_id"])
            chat_id = int(row["chat_id"])
            await pay_bot.kick_chat_member(channel_id, chat_id)
            await pay_bot.unban_chat_member(channel_id, chat_id)
            await database.update_user_subscribe_status(
                subscribe_channel_id=channel_id,
                chat_id=chat_id,
                subscribe_status="Expired",
                subscribe_status_previous="Active")
            N += 1
        elif row["paid_till"] < time + relativedelta.relativedelta(
                days=+2) and row["last_notify_time"] < time - relativedelta.relativedelta(days=+1):
            channel_id = int(str(row["subscribe_channel_id"])[4:])
            chat_id = int(row["chat_id"])
            text = "У вас заканчивается подписка на канал!\n"
            text += "Канал "
            text += hlink(f"{row['subscribe_channel']}\n",
                          f"https://t.me/c/{channel_id}/1")
            text += f"Срок подписки до <b>{row['paid_till']}</b>\n"
            try:
                await pay_bot.send_message(chat_id, text)
                await database.update_user_subscribe_last_notify_time(
                    last_notify_time=time,
                    subscribe_id=row["id"])
            except Exception as err:
                logging.exception(err)

    t2 = datetime.datetime.now()
    text = "Finish <b>kickChatMember</b> method\n"
    text += f"Kick N={N} users\n"
    time = t2 - t1
    text += f"Time: {time}\n"
    if message is not None:
        await message.answer(text=text)
    elif N > 0:
        for admin in ADMINS:
            await pay_bot.send_message(admin, text)
