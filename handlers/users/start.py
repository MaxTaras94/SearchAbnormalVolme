from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher import FSMContext
from states.choose_language import ChooseLanguageStates
from keyboards.inline.choose_language import choose_language
from loader import dp
from utils.db_api.db_commands import database


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    """
    Обработчик команды /start
    Добавляем нового юзера в бд.
    Показываем inline кнопки выбора языка.
    Устанавливаем состояние ChooseLanguageStates.Q1
    """
    await database.add_new_user()
    first_name = message.from_user.first_name
    # text = f"🇺🇸 Hi, {first_name} 😉\n"
    # text += "Please select the language 👇\n\n"
    # text += f"🇷🇺 Привет, {first_name} 😉\n"
    # text += "Выберите, пожалуйста, язык 👇"
    # await message.answer(text=text,
    #                      reply_markup=choose_language)
    # await state.finish()
    # await ChooseLanguageStates.Q1.set()

    text = f"🇺🇸 Hi, {first_name} 😉\n"
    text += f"🇷🇺 Привет, {first_name} 😉\n"
    await message.answer(text=text)