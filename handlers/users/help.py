from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp
from loader import dp


@dp.message_handler(CommandHelp(), state="*")
async def bot_help(message: types.Message):
    """
    /help функция бота.
    """
    text = "🇺🇸 List of bot commands:\n"
    text += "/start - bot start\n"
    text += "/help - bot help"
    text += "\n\n"
    text += "🇷🇺 Список команд бота:\n"
    text += "/start - Начать пользоваться ботом\n"
    text += "/help - Помощь по работе бота"
    await message.answer(text=text)
