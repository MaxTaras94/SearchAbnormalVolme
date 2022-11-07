# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 13:36:26 2021

@author: taras
"""



import datetime
from data.config import LOGINMT5, PASSMT5, SERVERMT5, path_to_terminal
from data.GenerateTextMessage import message_generator
from decimal import Decimal, ROUND_HALF_EVEN
import MetaTrader5 as mt5
import pandas as pd
import time
from SenderMessagesInChannel import sender


class UpdaterFOREX():
    
    """
    Данный класс создан для получения аномалий в объёмах и ценовых спрэдах
    для заданного списка инструментов напрямую от выбранного брокера путем
    интеграции через терминал MT5
    """
    
    def __init__(self):
        self.check_name = ['AUDUSD','EURGBP','EURJPY','EURUSD','GBPJPY',
        'GBPNZD','GBPUSD','NZDUSD','USDCAD','USDCHF','USDJPY','USDSGD',
        'XAGUSD','XAUUSD','FTSE100','IBEX35','NIKK225','SPX500','ASX200',
        'CAC40','HSI50','NG','NQ100','STOXX50','BRN','WTI','GER40',
        'GER40','NQ100','SPX500']
        self._cach = {'time':datetime.datetime.today(), 'tickers':{}}
        
    def initialize_terminal(self):
        status = mt5.initialize("C:/Program Files/Alpari MT5/terminal64.exe")
        if not status:
            i = 0
            while i < 10:
                status = mt5.initialize(path_to_terminal)
                if not status:
                    i += 1
                    time.sleep(1)
                    continue
                else:
                    break
        return status
    
    def __log_account_mt5(self):
        if self.initialize_terminal():
            return True
        else:
            self.initialize_terminal()
            st = mt5.login(LOGINMT5, password=PASSMT5, server=SERVERMT5)          
            return st
     
    def response_to_mt5(self, ticker, TF, index, count):
        dict_TF = {"M1": mt5.TIMEFRAME_M1,
                   "M5": mt5.TIMEFRAME_M5,
                   "M30": mt5.TIMEFRAME_M30,
                   "D1": mt5.TIMEFRAME_D1}
        return pd.DataFrame(mt5.copy_rates_from_pos(ticker, dict_TF[TF], index, count))
    
    async def forex_mm(self, ticker, rate_one_candle, rate_many_candles):
        delta = Decimal((rate_one_candle.tick_volume/rate_many_candles.tick_volume.median()).values[0]).quantize(Decimal("1.00"), ROUND_HALF_EVEN)
        spread_median = rate_many_candles.spread_candle.median()
        rate_one_candle['delta'] = delta
        high_density = Decimal((rate_one_candle.high_density/rate_many_candles.high_density.median()).values[0]).quantize(Decimal("1.00"), ROUND_HALF_EVEN)
        ratio_spread_vs_size_candle = Decimal((rate_one_candle.size_candle/rate_one_candle.spread_candle).values[0]).quantize(Decimal("1.00"), ROUND_HALF_EVEN)
        print(f"Состояние кэша на момент проверки: {self._cach}")
        if delta >= 6:
            if ticker not in self._cach['tickers']:
                self._cach['tickers'][ticker] = delta
                await sender.send_message(message_generator.abnormal_volume(rate_one_candle))
                # print(f'Найдена аномалия по паре {ticker} | Обнаруженный объём = {rate_one_candle.tick_volume.values[0]}  |  Дельта = {delta}   | Проторгованный объём за сегодня = {curr_vol}')
            elif ticker in self._cach['tickers'] and delta - self._cach['tickers'][ticker] >= 2:
                self._cach['tickers'][ticker] = delta
                await sender.send_message(message_generator.abnormal_volume(rate_one_candle))
            elif rate_one_candle.spread_candle.values[0]/spread_median > 15:
                await sender.send_message(message_generator.abnormal_price(rate_one_candle))
        elif high_density >= 5 and ratio_spread_vs_size_candle <= 1:
            await sender.send_message(message_generator.abnormal_density(rate_one_candle, high_density))
        else:
            print(f'По паре {ticker} аномалий не выявлено! delta = {delta} | текущий объём свечи:  {rate_one_candle.tick_volume.values[0]} | средний объём:  {rate_many_candles.tick_volume.mean()}')
        return True
  
    async def search_takeovers(self):
        if self.__log_account_mt5():
            try:
                for ticker in self.check_name:
                    print(f'Проверяю наличие поглощений для тикера {ticker}', end="\r")
                    candles_frame = self.response_to_mt5(ticker, "M30", 1, 2)
                    candles_frame['typeCandle'] = ['Bull' if candles_frame.loc[item, "open"] < candles_frame.loc[item, "close"] else 'Bear' for item in range(len(candles_frame))]
                    candles_frame['ticker'] = ticker
                    if candles_frame.loc[1, "close"] > candles_frame.loc[0, "open"] and candles_frame.loc[1, "typeCandle"] != candles_frame.loc[0, "typeCandle"]:
                        await sender.send_message(message_generator.bullish_takeover(candles_frame))
                    elif (candles_frame.loc[1, "close"] < candles_frame.loc[0, "open"] and candles_frame.loc[1, "typeCandle"] != candles_frame.loc[0, "typeCandle"]):
                        await sender.send_message(message_generator.bearish_takeover(candles_frame))
            except Exception as ke:
                print(f'Ошибка по тикеру {ticker}')
            
    
    async def checking_for_abnormal_volume_forex(self):
        if self.__log_account_mt5():
            time_now_for_checking = datetime.datetime.today().replace(second=0).replace(microsecond=0)# - datetime.timedelta(hours=1)
            if self._cach['time'] < datetime.datetime.today():
                self._cach['tickers'].clear()
                self._cach['time'] = datetime.datetime.today()
            try:
                for ticker in self.check_name:
                    print(f'Ищу аномалии по паре {ticker}', end="\r")
                    trade_tick_size = int(mt5.symbol_info(ticker)._asdict()['trade_tick_size']**(-1))
                    rate_one_candle = self.response_to_mt5(ticker, "M5", 1, 1)              
                    rate_one_candle['ticker'] = ticker
                    try:
                        rate_one_candle['time'] = pd.to_datetime(rate_one_candle['time'], unit='s')
                    except Exception as ke:
                        print(f'Ошибка пара {ticker} при конвертировании времени по инструменту {ticker}. Датафрейм свечи: {rate_one_candle}', exc_info=ke)
                        continue
                    time_curr_candle = pd.Timestamp(rate_one_candle['time'].values[0]).to_pydatetime()+datetime.timedelta(hours=1)
                    if rate_one_candle.empty:
                        print(f'Для пары {ticker} нет котировок. Датафрейм текущей свечи {rate_one_candle}')
                        continue  
                    rate_one_candle['ticker_name'] = ticker
                    rate_d1_candles = self.response_to_mt5(ticker, "D1", 1, 31)
                    try:
                        delta_price = float(Decimal(float((rate_one_candle.close - rate_d1_candles.close.values[-1])/rate_d1_candles.close.values[-1])*100).quantize(Decimal("1.00"), ROUND_HALF_EVEN))
                    except Exception as ae:
                        print(f'Ошибка по паре {ticker}', exc_info=ae)
                        continue
                    if (time_now_for_checking - time_curr_candle).seconds >= 600:
                        print(f'Для пары {ticker} последние данные по свече {time_curr_candle} Время проверки {time_now_for_checking}\nПерехожу к следующему инструменту в списке')
                        continue 
                    rate_many_candles = self.response_to_mt5(ticker, "M5", 0, 10000)
                    rate_many_candles['time'] = pd.to_datetime(rate_many_candles['time'], unit='s')
                    rate_many_candles['spread_candle'] = abs(rate_many_candles.open - rate_many_candles.close)*trade_tick_size
                    rate_many_candles['high_density'] = rate_many_candles.tick_volume/rate_many_candles.spread_candle
                    previously_candle = self.response_to_mt5(ticker, "M5", 2, 1)
                    try:
                        rate_one_candle['chg. price %'] = Decimal(float((rate_one_candle.close - previously_candle.close)/previously_candle.close)*100).quantize(Decimal("1.00"), ROUND_HALF_EVEN)
                    except Exception as ie:
                        print(f'Ошибка по паре {ticker} --- {ie}')
                        rate_one_candle['chg. price %'] = 0.00
                    rate_one_candle['chg. price_day %'] = Decimal(delta_price).quantize(Decimal("1.00"), ROUND_HALF_EVEN)
                    rate_one_candle['spread_candle'] = abs(rate_one_candle.open - rate_one_candle.close)*trade_tick_size
                    rate_one_candle['size_candle'] = abs(rate_one_candle.high - rate_one_candle.low)*trade_tick_size
                    rate_one_candle['candle_body'] = rate_one_candle.open > rate_one_candle.close
                    rate_one_candle['high_density'] = rate_one_candle.tick_volume/rate_one_candle.spread_candle
                    rate_one_candle['candle_body'] = rate_one_candle['candle_body'].replace(True, 'Bull').replace(False, 'Bear')
                    try:                                                 
                        print('Перехожу в блок функции forex_mm')
                        await self.forex_mm(ticker, rate_one_candle, rate_many_candles)
                    except Exception as ae:
                        print(f'Ошибка по паре {ticker} при выполнении ф-ции forex_mm --- {ae}')
                        continue
            except Exception as e:
                print(f'Ошибка по паре {ticker} --- {e}')
        else:
            print(f'Ошибка логининнга в МТ5: {mt5.last_error()}') 


updater_forex = UpdaterFOREX()
