from admin_loader import dp
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher import FSMContext


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    """
    Обработчик команды /start
    """
    first_name = message.from_user.first_name
    text = f"Привет, {first_name} 😉\n"
    await message.answer(text=text)
    await state.finish()
