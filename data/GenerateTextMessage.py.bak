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
            price_chg = "-" #str(row['chg. price %'].values[0])
        else:
            price_chg = "+" #+ str(row['chg. price %'].values[0])
        if row['chg. price_day %'].values[0] < 0:
            price_chg_day = str(row['chg. price_day %'].values[0])
        else:
            price_chg_day = "+" + str(row['chg. price_day %'].values[0])
        text = ""
        time = datetime.datetime.now().strftime("%H:%M:%S")
        candle_time = pd.to_datetime(row['time'], unit='s')[0].strftime("%d.%m.%Y %H:%M:%S")
        text += "⚠️ <u>Volume spike</u> 📊 <b>Ticker: #{row['ticker'].values[0].replace('&', '').replace('_i', '')}</b>\n\n"
        text += f"Abnormal volume growth: <b>{row['delta'].values[0]} times</b>\n"
        text += f"Price change within 5 minutes: <b>{price_chg+str(row['spread_candle'].values[0])} pips</b>\n"
        text += f"Today price change: <b>{price_chg_day}%</b>\n"
        text += f"Abnormal candle time: <b>{candle_time}</b>"
        return text
    
    def bullish_takeover(self, row):
        
        """Функция генерирует текст сообщения при бычьей поглощении"""
       
        text = ""
        time = datetime.datetime.now().strftime("%H:%M:%S")
        candle_time = pd.to_datetime(row['time'], unit='s')[0].strftime("%d.%m.%Y %H:%M:%S")
        text += f"<u>Бычье поглощение</u> 🟢 <b>Ticker: #{row['ticker'].values[0].replace('&', '').replace('_i', '')}</b>\n\n"
        text += f"Время свечи поглощения: <b>{candle_time}</b>"
        return text
    
    def bearish_takeover(self, row):
        
        """Функция генерирует текст сообщения при медвежьем поглощении"""
       
        text = ""
        time = datetime.datetime.now().strftime("%H:%M:%S")
        candle_time = pd.to_datetime(row['time'], unit='s')[0].strftime("%d.%m.%Y %H:%M:%S")
        text += f"<u>Медвежье поглощение</u> 🔴 <b>Ticker: #{row['ticker'].values[0].replace('&', '').replace('_i', '')}</b>\n\n"
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
        spread_candle = Decimal(row['spread_candle'].values[0]).quantize(Decimal('1.00'), ROUND_HALF_EVEN)
        spread_median = Decimal(row['spread_median'].values[0]).quantize(Decimal('1.00'), ROUND_HALF_EVEN)
        text = ""
        candle_time = pd.to_datetime(row['time'], unit='s').astype('str')[0]
        if row['chg. price %'].values[0] >= 0:
            text += f"⚠️ <u>Price growth</u> 📈 <b>Ticker: #{row['ticker'].values[0].replace('&', '').replace('_i', '')}</b>\n\n"
            text += f"Abnormal spread candle within 5 minutes: <b>{spread_candle} pips</b>\n"
            text += f"Median spread of last 30k 5 minutes candles: <b>{spread_median} pips/b>\n"
            text += f"Spread growth: <b>{spread_candle // spread_median} times</b>\n"
            text += f"Today price change: <b>{price_chg_day}%</b>\n"
            text += f"Abnormal candle time: <b>{candle_time}</b>"
        elif row['chg. price %'].values[0] <= 0:
            text += "⚠️ <u>Price drop</u> 📉 <b>Ticker: #{row['ticker'].values[0].replace('&', '').replace('_i', '')}</b>\n\n"
            text += f"Abnormal spread candle within 5 minutes: <b>{spread_candle} pips</b>\n"
            text += f"Median spread of last 30k 5 minutes candles: <b>{spread_median} pips/b>\n"
            text += f"Spread growth: <b>{spread_candle // spread_median} times</b>\n"
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
        spread_candle = Decimal(row['spread_candle'].values[0]).quantize(Decimal('1.00'), ROUND_HALF_EVEN)
        text = ""
        time = datetime.datetime.now().strftime("%H:%M:%S")
        candle_time = pd.to_datetime(row['time'], unit='s').astype('str')[0]
        text += f"⚠️ <u>High order density</u>🔝 <b>Ticker: #{row['ticker'].values[0].replace('&', '').replace('_i', '')}</b>\n\n"
        text += f"Spread candle within 5 minutes: <b>{spread_candle} pips</b>\n"
        text += f"Candle body: <b>{row['candle_body'].values[0]}</b>\n"
        text += f"Density growth: <b>{high_density} times</b>\n"
        text += f"Volume growth: <b>{row['delta'].values[0]} times</b>\n"
        text += f"Today price change: <b>{price_chg_day}%</b>\n"
        text += f"Abnormal candle time: <b>{candle_time}</b>"
        return text
    
message_generator = GenerateTextMessage()
