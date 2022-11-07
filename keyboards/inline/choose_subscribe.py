from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.callback_datas import choose_subscribe_callback


choose_subscribe = InlineKeyboardMarkup(row_width=1)
choose_subscribe.row()
choose_subscribe.insert(
    InlineKeyboardButton(text="На 1 мес за 1$",
                         callback_data=choose_subscribe_callback.new(
                             subscribe_period="month",
                             subscribe_price="1")))
choose_subscribe.insert(
    InlineKeyboardButton(text="На 1 год за 10$",
                         callback_data=choose_subscribe_callback.new(
                             subscribe_period="year",
                             subscribe_price="10")))
