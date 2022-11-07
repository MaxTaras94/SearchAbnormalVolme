from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.callback_datas import choose_channel_callback
from data.config import (RU_MM_TRADERHELPER_ID,
                         RU_QUOTE_TRADERHELPER_ID,
                         MM_TRADERHELPER_ID,
                         QUOTE_TRADERHELPER_ID)


choose_channel = InlineKeyboardMarkup(row_width=1)
choose_channel.row()
choose_channel.insert(
    InlineKeyboardButton(text="RU MM TraderHelper",
                         callback_data=choose_channel_callback.new(
                             channel="RU MM TraderHelper",
                             channel_id=RU_MM_TRADERHELPER_ID)))
choose_channel.insert(
    InlineKeyboardButton(text="RU QUOTE TraderHelper",
                         callback_data=choose_channel_callback.new(
                             channel="RU QUOTE TraderHelper",
                             channel_id=RU_QUOTE_TRADERHELPER_ID)))
choose_channel.insert(
    InlineKeyboardButton(text="MM TraderHelper",
                         callback_data=choose_channel_callback.new(
                             channel="MM TraderHelper",
                             channel_id=MM_TRADERHELPER_ID)))
choose_channel.insert(
    InlineKeyboardButton(text="QUOTE TraderHelper",
                         callback_data=choose_channel_callback.new(
                             channel="QUOTE TraderHelper",
                             channel_id=QUOTE_TRADERHELPER_ID)))
