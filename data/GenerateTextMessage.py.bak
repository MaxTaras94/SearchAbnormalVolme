# -*- coding: utf-8 -*-
"""
Данная ф-ция отвечает за генарцию текста сообщения для канала
"""

import datetime
from decimal import Decimal, ROUND_HALF_EVEN
import pandas as pd



class GenerateTextMessage():
    

    def abnormal_volume(self, row):
        
        """Функция генерирует текст сообщения при аномальном изменении объёма"""
       
        if row['chg. price %'].values[0] < 0:
            price_chg = str(row['chg. price %'].values[0])
        else:
            price_chg = "+" + str(row['chg. price %'].values[0])
        if row['chg. price_day %'].values[0] < 0:
            price_chg_day = str(row['chg. price_day %'].values[0])
        else:
            price_chg_day = "+" + str(row['chg. price_day %'].values[0])
        text = ""
        time = datetime.datetime.now().strftime("%H:%M:%S")
        text += f"<b>‼️ MARKET MOVEMENT  upd. {time}</b>\n\n"
        text += f"<b>Ticker: #{row['ticker'].values[0].replace('&', '').replace('_i', '')}</b>\n\n"
        candle_time = pd.to_datetime(row['time'], unit='s')[0].strftime("%d.%m.%Y %H:%M:%S")
        text += "⚠️ <u>Volume spike</u> 📊\n"
        text += f"Abnormal volume growth: <b>{row['delta'].values[0]} times</b>\n"
        text += f"Price change within 5 minutes: <b>{price_chg}%</b>\n"
        text += f"Today price change: <b>{price_chg_day}%</b>\n"
        text += f"Abnormal candle time: <b>{candle_time}</b>"
        return text
    
    def bullish_takeover(self, row):
        
        """Функция генерирует текст сообщения при бычьей поглощении"""
       
        text = ""
        time = datetime.datetime.now().strftime("%H:%M:%S")
        text += f"<b>‼️ MARKET MOVEMENT  upd. {time}</b>\n\n"
        text += f"<b>Ticker: #{row['ticker'].values[0].replace('&', '').replace('_i', '')}</b>\n\n"
        candle_time = pd.to_datetime(row['time'], unit='s')[0].strftime("%d.%m.%Y %H:%M:%S")
        text += "<u>Бычье поглощение</u> 🟢\n"
        text += f"Время свечи поглощения: <b>{candle_time}</b>"
        return text
    
    def bearish_takeover(self, row):
        
        """Функция генерирует текст сообщения при медвежьем поглощении"""
       
        text = ""
        time = datetime.datetime.now().strftime("%H:%M:%S")
        text += f"<b>‼️ MARKET MOVEMENT  upd. {time}</b>\n\n"
        text += f"<b>Ticker: #{row['ticker'].values[0].replace('&', '').replace('_i', '')}</b>\n\n"
        candle_time = pd.to_datetime(row['time'], unit='s')[0].strftime("%d.%m.%Y %H:%M:%S")
        text += "<u>Бычье поглощение</u> 🔴\n"
        text += f"Время свечи поглощения: <b>{candle_time}</b>"
        return text
        
    def abnormal_price(self, row):
        
        """Функция генерирует текст сообщения при аномальном изменении цены"""
        
        if row['chg. price %'].values[0] < 0:
            price_chg = str(row['chg. price %'].values[0])
        else:
            price_chg = "+" + str(row['chg. price %'].values[0])
        if row['chg. price_day %'].values[0] < 0:
            price_chg_day = str(row['chg. price_day %'].values[0])
        else:
            price_chg_day = "+" + str(row['chg. price_day %'].values[0])
        text = ""
        time = datetime.datetime.now().strftime("%H:%M:%S")
        text += f"<b>‼️ MARKET MOVEMENT  upd. {time}</b>\n\n"
        text += f"<b>Ticker: #{row['ticker'].values[0].replace('&', '').replace('_i', '')}</b>\n\n"
        candle_time = pd.to_datetime(row['time'], unit='s').astype('str')[0]
        if row['chg. price %'].values[0] >= 0:
            text += "⚠️ <u>Price growth</u> 📈\n"
            text += f"Abnormal spread candle within 5 minutes: <b>{price_chg}%</b>\n"
            text += f"Volume growth: <b>{row['delta'].values[0]} times</b>\n"
            text += f"Today price change: <b>{price_chg_day}%</b>\n"
            text += f"Abnormal candle time: <b>{candle_time}</b>"
        elif row['chg. price %'].values[0] <= 0:
            text += "⚠️ <u>Price drop</u> 📉\n"
            text += f"Abnormal spread candle within 5 minutes: <b>{price_chg}%</b>\n"
            text += f"Volume growth: <b>{Decimal(row['delta'].values[0]).quantize(Decimal('1.00'), ROUND_HALF_EVEN)} times</b>\n"
            text += f"Today price change: <b>{price_chg_day}%</b>\n"
            text += f"Abnormal candle time: <b>{candle_time}</b>"
        return text
    
    
    def abnormal_density(self, row, high_density):
        
        """Функция генерирует текст сообщения при относительно высоком тиковом объёме и очень маленьком ценовом спрэде"""
        
        if row['chg. price %'].values[0] < 0:
            price_chg = str(row['chg. price %'].values[0])
        else:
            price_chg = "+" + str(row['chg. price %'].values[0])
        if row['chg. price_day %'].values[0] < 0:
            price_chg_day = str(row['chg. price_day %'].values[0])
        else:
            price_chg_day = "+" + str(row['chg. price_day %'].values[0])
        text = ""
        time = datetime.datetime.now().strftime("%H:%M:%S")
        text += f"<b>‼️ MARKET MOVEMENT  upd. {time}</b>\n\n"
        text += f"<b>Ticker: #{row['ticker'].values[0].replace('&', '').replace('_i', '')}</b>\n\n"
        candle_time = pd.to_datetime(row['time'], unit='s').astype('str')[0]
        text += "⚠️ <u>High order density</u>🔝\n"
        text += f"Spread candle within 5 minutes: <b>{Decimal(row['spread_candle'].values[0]).quantize(Decimal('1.00'), ROUND_HALF_EVEN)}</b>\n"
        text += f"Candle body: <b>{row['candle_body'].values[0]}</b>\n"
        text += f"Density growth: <b>{high_density} times</b>\n"
        text += f"Volume growth: <b>{row['delta'].values[0]} times</b>\n"
        text += f"Today price change: <b>{price_chg_day}%</b>\n"
        text += f"Abnormal candle time: <b>{candle_time}</b>"
        return text
    
message_generator = GenerateTextMessage()
