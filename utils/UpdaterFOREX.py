# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 21:47:59 2021

@author: TarMS
"""

from data.config import SERVER, DBUSERNAME_BACK, DBPASSWORD_BACK, DATABASE, LOGINMT5, PASSMT5, SERVERMT5
import datetime
from decimal import Decimal, ROUND_HALF_EVEN
import MetaTrader5 as mt5
import pandas as pd
import pymysql
import time
from utils.Logger import Logger



class UpdaterFOREX():
    """
    Данный класс создан для получения аномалий в объёмах и ценовых спрэдах
    для заданного списка инструментов напрямую Amarkets
    """
    
    def __init__(self):
        self._log_errors = Logger('UpdaterFOREX', 'logs back/FOREX/Errors/', 'ERROR').create_logger()
        self._log_warnings = Logger('UpdaterFOREX', 'logs back/FOREX/Warnings/', 'WARNING').create_logger()
        self._logs = Logger('UpdaterFOREX', 'logs back/FOREX/Info/', 'DEBUG').create_logger()
        self._logs.info('UpdaterFOREX запустился')
    
    def initialize_terminal(self):
        self._logs.info('Провожу инициализацию терминала МТ5')
        status = mt5.initialize()
        if not status:
            i = 0
            while i < 10:
                status = mt5.initialize()
                if not status:
                    i += 1
                    time.sleep(1)
                    continue
                else:
                    break
        self.check_name = [pair.name for pair in mt5.symbols_get()]
        return status
    
    def __log_account_mt5(self):
        if self.initialize_terminal():
            return True
        else:
            self.initialize_terminal()
            self._logs.info('Логинюсь в терминале МТ5')
            st = mt5.login(LOGINMT5, password=PASSMT5, server=SERVERMT5)
            
            self._logs.debug('Успех: логиннинг в терминале прошел успешно, перехожу к поиску аномалий')
            return st
     
    def response_to_mt5(self, ticker, TF, index, count):
        dict_TF = {"M1": mt5.TIMEFRAME_M1,
                   "M5": mt5.TIMEFRAME_M5,
                   "D1": mt5.TIMEFRAME_D1}
        return pd.DataFrame(mt5.copy_rates_from_pos(ticker, dict_TF[TF], index, count))
    
    def __db_insert_mm(self, ticker, rate_one_candle, rate_many_candles, rate_d1_candles):
        delta = Decimal(float(rate_one_candle.tick_volume.values[0])/float(rate_many_candles.tick_volume.mean()/520)).quantize(Decimal("1"), ROUND_HALF_EVEN)
        curr_vol = rate_many_candles.tick_volume.mean()
        if delta >= 5:         
            rate_one_candle['delta'] = delta
            self._log_warnings.warning(f'Найдена аномалия по паре {ticker} | Обнаруженный объём = {rate_one_candle.tick_volume.values[0]}  |  Дельта = {delta}   | Проторгованный объём за сегодня = {curr_vol}')    
            db_global_forex.insert_market_movement_moex(ticker, rate_one_candle.ticker_name.values[0], rate_one_candle.tick_volume.values[0], rate_one_candle.delta.values[0], Decimal(float(rate_many_candles.tick_volume.mean()/520)).quantize(Decimal("1"), ROUND_HALF_EVEN), Decimal(float(rate_d1_candles.tick_volume.mean())).quantize(Decimal("1"), ROUND_HALF_EVEN), rate_one_candle.close.values[0], Decimal(float(rate_one_candle['chg. price %'].values[0])).quantize(Decimal("1.00"), ROUND_HALF_EVEN), Decimal(float(rate_one_candle['chg. price_day %'].values[0])).quantize(Decimal("1.00"), ROUND_HALF_EVEN), pd.Timestamp(rate_one_candle['time'].values[0]).to_pydatetime())
        else:
            self._logs.info(f'По паре {ticker} аномалий не выявлено! Проторговано за сегодня:  {curr_vol}  |  delta = {delta}  |  текущий объём свечи:  {rate_one_candle.tick_volume.values[0]}  | средний объём:  {rate_many_candles.tick_volume.mean()/520}')
        return True
    
    def checking_for_abnormal_volume_forex(self):
        if self.__log_account_mt5():
            time_now_for_checking = datetime.datetime.today().replace(second=0).replace(microsecond=0)
            self.growth_leaders = {}
            self.fall_leaders = {}
            try:
                for ticker in self.check_name:
                    print(f'Ищу аномалии по паре {ticker}', end="\r")
                    rate_one_candle = self.response_to_mt5(ticker, "M1", 1, 1)              
                    rate_one_candle['ticker'] = ticker
                    try:
                        rate_one_candle['time'] = pd.to_datetime(rate_one_candle['time'], unit='s')
                    except KeyError as ke:
                        self._log_errors.exception(f'Ошибка пара {ticker} при конвертировании времени по инструменту {ticker}. Датафрейм свечи: {rate_one_candle}', exc_info=ke)
                        continue
                    time_curr_candle = pd.Timestamp(rate_one_candle['time'].values[0]).to_pydatetime()
                    if rate_one_candle.empty:
                        self._log_warnings.warning(f'Для пары {ticker} нет котировок. Датафрейм текущей свечи {rate_one_candle}')
                        continue  
                    rate_one_candle['ticker_name'] = ticker
                    rate_d1_candles = self.response_to_mt5(ticker, "D1", 1, 31)
                    try:
                        delta_price = float(Decimal(float((rate_one_candle.close - rate_d1_candles.close.values[-1])/rate_d1_candles.close.values[-1])*100).quantize(Decimal("1.00"), ROUND_HALF_EVEN))
                    except AttributeError as ae:
                        self._log_errors.exception(f'Ошибка по паре {ticker}', exc_info=ae)
                        continue
                    if delta_price > 0:
                        self.growth_leaders[ticker] = [delta_price, float(rate_one_candle.close.values[0]), rate_one_candle.ticker_name.values[0]]
                    elif delta_price < 0:
                        self.fall_leaders[ticker] = [delta_price, float(rate_one_candle.close.values[0]), rate_one_candle.ticker_name.values[0]]
                    else:
                        pass
                    if (time_now_for_checking - time_curr_candle).seconds > 120:
                        print(f'Для пары {ticker} последние данные по свече {time_curr_candle} Время проверки {time_now_for_checking}\nПерехожу к следующему инструменту в списке')
                        self._log_warnings.warning(f'Для пары {ticker} последние данные по свече {time_curr_candle}. Время проверки {time_now_for_checking}')
                        continue 
                    rate_many_candles = self.response_to_mt5(ticker, "D1", 1, 31)
                    rate_many_candles['time'] = pd.to_datetime(rate_many_candles['time'], unit='s')
                    rate_one_candle['avg. volume'] = rate_many_candles.tick_volume.mean()/520
                    previously_candle = self.response_to_mt5(ticker, "M1", 2, 1)
                    try:
                        rate_one_candle['chg. price %'] = Decimal(float((rate_one_candle.close - previously_candle.close)/previously_candle.close)*100).quantize(Decimal("1.00"), ROUND_HALF_EVEN)
                    except IndexError as ie:
                        self._log_errors.exception(f'Ошибка по паре {ticker}', exc_info=ie)
                        rate_one_candle['chg. price %'] = 0.00
                    rate_one_candle['chg. price_day %'] = Decimal(delta_price)
                    try:                                                 
                        print('Перехожу в блок функции __db_insert_mm')
                        self.__db_insert_mm(ticker, rate_one_candle, rate_many_candles, rate_d1_candles)
                    except AttributeError as ae:
                        self._log_errors.exception('Ошибка по паре {ticker}', exc_info=ae)
                        continue
            except Exception as e:
                self._log_errors.exception('Ошибка по паре {ticker}', exc_info=e)
        else:
            self._log_errors.error('Ошибка логининнга в МТ5: {mt5.last_error()}') 
            


class DBCommandsGLOBALforForex:
    """
    Класс для взаимодействия с базой данных MOEX.
    В __init__ прописаны SQL запросы,
    которые ниже реализованы в качестве методов.
    """

    def __init__(self):
        self.__INSERT_MARKET_MOVEMENT_FOREX = "INSERT INTO DataMMForex (id, ticker, ticker_name, vol_lots, vol_chg, avg_m5_volume, avg_daily_volume, price, price_chg, price_chg_day, candle_time, time) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())"
        self._log_errors = Logger('DBCommandsGLOBALforForex', 'logs back/DBGLOBAL/Errors/', 'ERROR').create_logger()
        self._logs = Logger('DBCommandsGLOBALforForex', 'logs back/DBGLOBAL/INFO/', 'DEBUG').create_logger()
        self.conn = self.__initialize()
        
    def __db_create_connection(self):
        return pymysql.connect(
            host=SERVER,
            user=DBUSERNAME_BACK,
            password=DBPASSWORD_BACK,
            db=DATABASE)    
            
    def __initialize(self):
        try:
            conn = self.__db_create_connection()
            self._logs.info('DB Hoster has connected')
            return conn
        except Exception as err:
            self._log_errors.exception('Ошибка инициализации БД', exc_info=err)
            pass
    
    def write_to_db(self, command, args):
        self.conn.ping(reconnect=True)
        conn = self.conn
        cur = conn.cursor()
        cur.execute(command, args)
        conn.commit()
        conn.close()

    def insert_market_movement_forex(self, ticker, ticker_name, vol_lots, vol_chg, avg_m5_volume, avg_daily_volume, price, price_chg, price_chg_day, candle_time):
        command = self.__INSERT_MARKET_MOVEMENT_FOREX
        args = ticker, ticker_name, vol_lots, vol_chg, avg_m5_volume, avg_daily_volume, price, price_chg, price_chg_day, candle_time
        print(f'Вызван метод insert_market_movement_forex, переданы аргументы {args}')
        self.write_to_db(command, args)

db_global_forex = DBCommandsGLOBALforForex()        
updater_forex = UpdaterFOREX()
