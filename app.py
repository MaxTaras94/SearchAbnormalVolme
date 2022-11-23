# -*- coding: utf-8 -*-
'''
Главный модуль для запуска бота
'''


import aiogram
from aiogram import executor
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from data.config import LOGINMT5, PASSMT5, SERVERMT5, path_to_terminal
from decimal import Decimal, ROUND_HALF_EVEN
from loader import bot, dp, storage
import MetaTrader5 as mt5
# import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify, on_shutdown_notify #оповещение админов о начале/окончании работы Бота
from utils.ForexDataUpdater import ForexUpdater



async def on_startup(dp):
    global forex_updater
    # Уведомляет про запуск
    await on_startup_notify(bot)
    # Запускаем обновление канала
    mt5.initialize()
    mt5.login(LOGINMT5, password=PASSMT5, server=SERVERMT5)
    forex_updater = ForexUpdater()
    # filters.setup(dp)
    # middlewares.setup(dp)

@dp.message_handler(commands=['start'])
async def process_hi1_command(message: aiogram.types.Message):
    button_equity = KeyboardButton('Equity')
    button_balance = KeyboardButton('Balance')
    button_calc_risk = KeyboardButton('Calculate Risk')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(button_equity,button_balance).add(button_calc_risk)
    await message.reply("Добро пожаловать!", reply_markup=keyboard)

@dp.message_handler(text=['Equity'])
async def requests_equity(callback_query: aiogram.types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Equity: {}".format(f"{mt5.account_info()._asdict()['equity']:,.2f}".replace(',', ' ')))

@dp.message_handler(text=['Balance'])
async def requests_balance(callback_query: aiogram.types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Balance: {}".format(f"{mt5.account_info()._asdict()['balance']:,.2f}".replace(',', ' ')))

@dp.message_handler(text=['Calculate Risk'])
async def requests_balance(callback_query: aiogram.types.CallbackQuery):
    list_buttons = []
    for ticker in sorted(forex_updater.check_name):
        list_buttons.append(InlineKeyboardButton(ticker, callback_data=ticker))
    ticker_buttons = InlineKeyboardMarkup()
    for button in list_buttons:
        ticker_buttons.insert(button)
    await bot.send_message(callback_query.from_user.id, "Выбери инструмент", reply_markup=ticker_buttons)

@dp.callback_query_handler(lambda c: c.data and not c.data.startswith('btn_'))
async def callback_one_of_the_tickers(callback_query: aiogram.types.CallbackQuery):
    global ticker   
    ticker = callback_query.data
    await bot.send_message(callback_query.from_user.id, f'Выбор пал на <b>{ticker}</b>\nУкажи размер риска в пунктах')

@dp.message_handler(lambda message: '.' in message.text or ',' in message.text)
async def risk_pips(message: aiogram.types.Message):
    global pips
    pips = float(message.text.replace(',', '.'))
    list_risk = ['1', '2', '3', '5', '10', '20', '30', '40', '50', '60']
    list_risk_buttons = []
    for risk_perc in list_risk:
        list_risk_buttons.append(InlineKeyboardButton(risk_perc, callback_data='btn_'+risk_perc))
    risk_buttons = InlineKeyboardMarkup()
    for risk in list_risk_buttons:
        risk_buttons.insert(risk)
    await bot.send_message(message.chat.id, f'Выбор пал на <b>{ticker}</b>\nРазмер риска в пунктах: <b>{pips}</b>\nВыбери каким % от Equity рискнешь', reply_markup=risk_buttons)
    
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn_'))
async def callback_one_of_the_tickers(callback_query: aiogram.types.CallbackQuery):
    perc_risk = callback_query.data
    print(ticker)
    data_for_ticker = mt5.symbol_info(ticker)._asdict()
    trade_tick_value = data_for_ticker.get('trade_tick_value', 0)
    volume_min = data_for_ticker.get('volume_min', 0)
    price_of_tick = 10*volume_min
    risk_size = int(float(mt5.account_info()._asdict()["equity"])*(float(perc_risk.split("_")[1])/100))
    trade_lot = Decimal(volume_min*(risk_size/(price_of_tick*pips))).quantize(Decimal("1.00"), ROUND_HALF_EVEN)
    margin = mt5.order_calc_margin(mt5.ORDER_TYPE_SELL, ticker, trade_lot, data_for_ticker.get('bid', 0))
    await bot.send_message(callback_query.from_user.id, f'Тикер: <b>{ticker}</b>\nРиск в % от Equity:  <b>{int(perc_risk.split("_")[1])}</b>\nРиск в $ от Equity: <b>{str(risk_size)}</b>\nРиск в пунктах: <b>{pips}</b>\nЛот для входа в сделку: <b>{trade_lot}</b>\nМаржа: <b>{margin}</b>')

async def on_shutdown(dp):
    await on_shutdown_notify(bot)
    await bot.close()
    await storage.close()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)