from loader import dp
from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext
from states.choose_language import ChooseLanguageStates
from utils.db_api.db_commands import database
from handlers.users.newsubscribe import newsubscribe


@dp.callback_query_handler(text_contains="lang_",
                           state=ChooseLanguageStates.Q1)
async def lang1(call: CallbackQuery, state: FSMContext):
    """
    Обрабатываем выбор языка через inline кнопки.
    Обновляем данные о юзере в бд.
    Закрываем состояние ChooseLanguageStates.Q1
    """
    await call.answer(cache_time=1)
    lang = call.data.split(':')[1]
    await database.update_user_lang(lang)
    if lang == "eng":
        text = "🇺🇸 Nice, you choose <b>English</b>!\n"
        await call.message.answer(text=text)
    else:
        text = "🇷🇺 Отлично, Вы выбрали <b>Русский язык</b>!\n"
        await call.message.answer(text=text)
    await state.finish()

    # Моделируем нажание команды /newsubscribe
    await newsubscribe(call.message, state)


@dp.message_handler(state=ChooseLanguageStates.Q1)
async def lang2(message: Message, state: FSMContext):
    """
    Выбрать язык можно только через inline кнопки.
    Если приходит какой-то текст - просим кликнуть на кнопки с языком.
    """
    text = "🇺🇸 For English language, click on the button \"English\" ☝\n\n"
    text += "🇷🇺 Для выбора русского языка нажмите на кнопку \"Русский\" ☝"
    await message.answer(text=text)
