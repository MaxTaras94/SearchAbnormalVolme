# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 21:47:59 2021

@author: TarMS
"""

from data import config
import datetime
from decimal import Decimal, ROUND_HALF_EVEN
import MetaTrader5 as mt5
import pandas as pd
import time
from utils.db_api.db_commands_back import db_global
from utils.Logger import Logger

class UpdaterMOEX():
    """
    Данный класс создан для получения аномалий в объёмах и ценовых спрэдах
    для заданного списка инструментов напрямую ММВБ
    """
    
    def __init__(self):
        self._check_name = pd.read_excel(r'C:\Users\Администратор\Documents\Parsing_MICEX.xlsx', sheet_name='TQBR')
        self._log_errors = Logger('UpdaterMOEX', 'logs back/MOEX/Errors/', 'ERROR').create_logger()
        self._log_warnings = Logger('UpdaterMOEX', 'logs back/MOEX/Warnings/', 'WARNING').create_logger()
        self._logs = Logger('UpdaterMOEX', 'logs back/MOEX/Info/', 'DEBUG').create_logger()
        self._logs.info('UpdaterMOEX запустился')
        self._check_time_candle = {}
    
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
        return status
    
    def __log_account_mt5(self):
        if self.initialize_terminal():
            return True
        else:
            self.initialize_terminal()
            self._logs.info('Логинюсь в терминале МТ5')
            st = mt5.login(config.LOGINMICEXMT5, password=config.PASSMICEXMT5, server=config.SERVERMICEXMT5)
            self._logs.debug('Успех: логиннинг в терминале прошел успешно, перехожу к поиску аномалий')
            return st
     
    def response_to_mt5(self, ticker, TF, index, count):
        dict_TF = {"M1": mt5.TIMEFRAME_M1,
                   "M5": mt5.TIMEFRAME_M5,
                   "D1": mt5.TIMEFRAME_D1}
        return pd.DataFrame(mt5.copy_rates_from_pos(ticker, dict_TF[TF], index, count))
    
    def __db_insert_mm(self, ticker, rate_one_candle, rate_many_candles, rate_d1_candles):
        delta = Decimal(float(rate_one_candle.real_volume.values[0])/float(rate_many_candles.real_volume.mean()/520)).quantize(Decimal("1"), ROUND_HALF_EVEN)
        curr_vol = rate_many_candles.real_volume.mean()
        time_candle = pd.Timestamp(rate_one_candle['time'].values[0]).to_pydatetime()
        try:
            self._check_time_candle[ticker]
        except KeyError:
            self._check_time_candle[ticker] = ''
        if delta >= 20 and curr_vol > 10000 and self._check_time_candle[ticker] != time_candle:         
            rate_one_candle['delta'] = delta
            self._log_warnings.warning(f'Найдена аномалия по акции {ticker} | Обнаруженный объём = {rate_one_candle.real_volume.values[0]}  |  Дельта = {delta}   | Проторгованный объём за сегодня = {curr_vol}')    
            self._check_time_candle[ticker] = time_candle
            db_global.insert_market_movement_moex(ticker, rate_one_candle.ticker_name.values[0], rate_one_candle.real_volume.values[0], rate_one_candle.delta.values[0], Decimal(float(rate_many_candles.real_volume.mean()/520)).quantize(Decimal("1"), ROUND_HALF_EVEN), Decimal(float(rate_d1_candles.real_volume.mean())).quantize(Decimal("1"), ROUND_HALF_EVEN), rate_one_candle.close.values[0], Decimal(float(rate_one_candle['chg. price %'].values[0])).quantize(Decimal("1.00"), ROUND_HALF_EVEN), Decimal(float(rate_one_candle['chg. price_day %'].values[0])).quantize(Decimal("1.00"), ROUND_HALF_EVEN), time_candle)
        else:
            #self._logs.info(f'По тикеру {ticker} аномалий не выявлено: проторговано за сегодня:  {curr_vol}\ndelta = {delta}\nтекущий объём свечи:  {rate_one_candle.real_volume.values[0]}\nсредний объём:  {rate_many_candles.real_volume.mean()/520}\nвремя проверяемой свечи -- {time_candle}\nвремя последней свечи - {time_candle}\nвремя предыдущей аномальной свечи -- {self._check_time_candle[ticker]}')
            print(f'По тикеру {ticker} аномалий не выявлено: проторговано за сегодня:  {curr_vol}\ndelta = {delta}\nтекущий объём свечи:  {rate_one_candle.real_volume.values[0]}\nсредний объём:  {rate_many_candles.real_volume.mean()/520}\nвремя проверяемой свечи -- {time_candle}\nвремя последней свечи - {time_candle}\nвремя предыдущей аномальной свечи -- {self._check_time_candle[ticker]}')
        return True
    
    def checking_for_abnormal_volume_moex(self):
        if self.__log_account_mt5():
            check_name = self._check_name.Code_stock.to_list()
            time_now_for_checking = datetime.datetime.today().replace(second=0).replace(microsecond=0)
            self.growth_leaders = {}
            self.fall_leaders = {}
            try:
                for ticker in check_name:
                    print(f'Ищу аномалии по интструменту {ticker}', end="\r")
                    rate_one_candle = self.response_to_mt5(ticker, "M1", 1, 1)              
                    rate_one_candle['ticker'] = ticker
                    try:
                        rate_one_candle['time'] = pd.to_datetime(rate_one_candle['time'], unit='s')
                    except KeyError as ke:
                        #self._log_errors.exception(f'Ошибка тикер {ticker} при конвертировании времени по инструменту {ticker}. Датафрейм свечи: {rate_one_candle}', exc_info=ke)
                        print(f'Ошибка тикер {ticker} при конвертировании времени по инструменту {ticker}. Датафрейм свечи: {rate_one_candle}', exc_info=ke)
                        continue
                    time_curr_candle = pd.Timestamp(rate_one_candle['time'].values[0]).to_pydatetime()
                    if rate_one_candle.empty:
                        #self._log_warnings.warning(f'Для инструмента {ticker} нет котировок. Датафрейм текущей свечи {rate_one_candle}')
                        print(f'Для инструмента {ticker} нет котировок. Датафрейм текущей свечи {rate_one_candle}')
                        continue  
                    rate_one_candle['ticker_name'] = self._check_name.Name_stock[check_name.index(ticker)]
                    rate_d1_candles = self.response_to_mt5(ticker, "D1", 1, 31)
                    try:
                        delta_price = float(Decimal(float((rate_one_candle.close - rate_d1_candles.close.values[-1])/rate_d1_candles.close.values[-1])*100).quantize(Decimal("1.00"), ROUND_HALF_EVEN))
                    except AttributeError as ae:
                        #self._log_errors.exception(f'Ошибка по тикеру {ticker}', exc_info=ae)
                        print(f'Ошибка по тикеру {ticker}, {ae}')
                        continue
                    if delta_price > 0:
                        self.growth_leaders[ticker] = [delta_price, float(rate_one_candle.close.values[0]), rate_one_candle.ticker_name.values[0]]
                    elif delta_price < 0:
                        self.fall_leaders[ticker] = [delta_price, float(rate_one_candle.close.values[0]), rate_one_candle.ticker_name.values[0]]
                    else:
                        pass
                    if (time_now_for_checking - time_curr_candle).seconds > 120:
                        #self._log_warnings.warning(f'Для инструмента {ticker} последние данные по свече {time_curr_candle}. Время проверки {time_now_for_checking}')
                        print(f'Для инструмента {ticker} последние данные по свече {time_curr_candle}. Время проверки {time_now_for_checking}')
                        continue 
                    rate_many_candles = self.response_to_mt5(ticker, "D1", 1, 31)
                    rate_many_candles['time'] = pd.to_datetime(rate_many_candles['time'], unit='s')
                    rate_one_candle['avg. volume'] = rate_many_candles.real_volume.mean()/520
                    previously_candle = self.response_to_mt5(ticker, "M1", 2, 1)
                    try:
                        rate_one_candle['chg. price %'] = Decimal(float((rate_one_candle.close - previously_candle.close)/previously_candle.close)*100).quantize(Decimal("1.00"), ROUND_HALF_EVEN)
                    except IndexError as ie:
                        #self._log_errors.exception(f'Ошибка по тикеру {ticker}', exc_info=ie)
                        print(f'Ошибка по тикеру {ticker}, {ie}')
                        rate_one_candle['chg. price %'] = 0.00
                    rate_one_candle['chg. price_day %'] = Decimal(delta_price)
                    try:                                                 
                        print('Перехожу в блок функции __db_insert_mm')
                        self.__db_insert_mm(ticker, rate_one_candle, rate_many_candles, rate_d1_candles)
                    except AttributeError as ae:
                        #self._log_errors.exception('Ошибка по тикеру {ticker}', exc_info=ae)
                        print(f'Ошибка по тикеру {ticker}, {ae}')
                        continue
            except Exception as e:
                #self._log_errors.exception('Ошибка по тикеру {ticker}', exc_info=e)
                print(f'Ошибка по тикеру {ticker}, {e}')
        else:
            #self._log_errors.error('Ошибка логининнга в МТ5: {mt5.last_error()}') 
            print('Ошибка логининнга в МТ5: {mt5.last_error()}') 
            
            
updater_moex = UpdaterMOEX()