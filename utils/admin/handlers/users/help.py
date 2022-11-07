from admin_loader import dp
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp


@dp.message_handler(CommandHelp(), state="*")
async def bot_help(message: types.Message):
    """
    /help функция бота.
    """
    text = "Список команд бота:\n"
    text += "/start - Начать пользоваться ботом\n"
    text += "/help - Помощь по работе бота\n"
    text += "/kickusers - Удалить протухших юзеров\n"
    await message.answer(text=text)
