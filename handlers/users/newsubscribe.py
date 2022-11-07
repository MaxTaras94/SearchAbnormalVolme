from loader import dp
from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from states.newsubscribe import NewSubscribeStates
from utils.db_api.db_commands import database
from keyboards.inline.choose_channel import choose_channel


@dp.message_handler(Command("newsubscribe"), state="*")
async def newsubscribe(message: Message, state: FSMContext):
    """
    Показываем inline кнопки для выбор каналов для оплаты.
    Устанавливаем состояние NewSubscribeStates.Q1
    """
    await state.finish()
    await NewSubscribeStates.Q1.set()

    text = "Выберите канал доступ к которому хотите оплатить:"
    await message.answer(text=text,
                         reply_markup=choose_channel)
