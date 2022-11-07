from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.callback_datas import choose_language_callback


choose_language = InlineKeyboardMarkup(row_width=2)
choose_language.row()
choose_language.insert(
    InlineKeyboardButton(text="English",
                         callback_data=choose_language_callback.new(
                             language="eng")))
choose_language.insert(
    InlineKeyboardButton(text="Русский",
                         callback_data=choose_language_callback.new(
                             language="rus")))
