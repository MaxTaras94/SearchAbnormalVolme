# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 21:47:59 2021

@author: TarMS
"""

import datetime
from decimal import Decimal, ROUND_HALF_EVEN
import pandas as pd
import time
from utils.db_api.db_commands_back import db_global, db_local
from utils.Logger import Logger

class UpdaterSPIMEX:
    """
    Класс для обновления данных по Питерской бирже.
    """
    def __init__(self):
        self._count = 0 #переменная для счетчика
        self._from_spb = pd.DataFrame()
        self._log_errors = Logger('UpdaterSPIMEX', 'logs back/SPIMEX/Errors/', 'ERROR').create_logger()
        self._log_warnings = Logger('UpdaterSPIMEX', 'logs back/SPIMEX/Warnings/', 'WARNING').create_logger()
        self._logs = Logger('UpdaterSPIMEX', 'logs back/SPIMEX/Info/', 'DEBUG').create_logger()
        self._logs.info('UpdaterSPIMEX запустился')

    def _counter(self):
        """Функция-счётчик
        Просто увеличивает переменную _count объекта класса на 1 при вызове"""
        self._count += 1
        return self._count 

    def _spb_mm(self):
        """Главная функция текущего класса.
        Она выполняет обработку данных из бэкап-базы, проверяет данные по каждой акции в списке и возвращает расчётный фрейм с данными по объёму текущей 5-ти минутной свечи для каждого тикера.
        Функция вызывается автоматически из другого класса каждые 5 минут."""
        command = db_local.GET_FROM_DB_BACKUP
        count = self._counter()
        if count == 1:
            #self._logs.info(f'Вызвана функция _spb_mm, вызов #{count}')
            print(f'Вызвана функция _spb_mm, вызов #{count}')
            data_df = pd.DataFrame()
            data_df = data_df.append(db_local.get_from_db_fetchall(command))
            data_df['m5_volume'] = ''
            data_df['m5_chg_price_prc'] = ''
            data_df['chg_price_per'] = ''
            self._from_spb = self._from_spb.append(data_df.set_index('ticker'))
            return [self._from_spb, count]
        else:
            #self._logs.info(f'Вызвана функция _spb_mm, вызов #{count}')
            print(f'Вызвана функция _spb_mm, вызов #{count}')
            data_df = pd.DataFrame()
            data_df = data_df.append(db_local.get_from_db_fetchall(command))
            data_df = data_df.set_index('ticker')
            if len(data_df) <= len(self._from_spb):
                #self._logs.info('Длина data_df <= self._from_spb, поэтому выполняю 1-ый блок')
                print('Длина data_df <= self._from_spb, поэтому выполняю 1-ый блок')
                self._from_spb['m5_volume'].update(data_df['volume'] - self._from_spb['volume'])
                self._from_spb['m5_chg_price_prc'].update((data_df.price_last_deal - self._from_spb.price_last_deal)/self._from_spb.price_last_deal*100)
                self._from_spb['chg_price_per'].update((data_df.price_last_deal - self._from_spb.price_open)/self._from_spb.price_open*100)
                self._from_spb['volume'].update(data_df['volume'])
                self._from_spb['time_of_last_change'].update(data_df['time_of_last_change'])
                self._from_spb['price_last_deal'].update(data_df['price_last_deal'])
                return [self._from_spb, count]
            else:
                #self._logs.info(f'Длина data_df > self._from_spb, поэтому выполняю 2-ой блок')
                print(f'Длина data_df > self._from_spb, поэтому выполняю 2-ой блок')
                self._from_spb = (self._from_spb.append(data_df[~data_df.index.isin(self._from_spb.index)]))
                self._from_spb['m5_volume'].update(data_df['volume'] - self._from_spb['volume'])
                self._from_spb['m5_chg_price_prc'].update((data_df.price_last_deal - self._from_spb.price_last_deal)/self._from_spb.price_last_deal*100)
                self._from_spb['chg_price_per'].update((data_df.price_last_deal - self._from_spb.price_close)/self._from_spb.price_close*100)
                self._from_spb['volume'].update(data_df['volume']) 
                self._from_spb['time_of_last_change'].update(data_df['time_of_last_change']) 
                self._from_spb['price_last_deal'].update(data_df['price_last_deal'])                
                return [self._from_spb, count]          
            
    def checking_for_abnormal_volume_spimex(self):
        """Функция получает фрейм из функции _spb_mm и проверяет аномалии на объёмах свечей.
        В случае выявления аномалии записывает соответствующие данные в БД"""
        #self._logs.debug('Начал поиск аномалий по СПБ бирже')
        print('Начал поиск аномалий по СПБ бирже')
        data_for_check = self._spb_mm()   
        time_now_for_checking = datetime.datetime.today().replace(second=0).replace(microsecond=0)
        if data_for_check[1]  == 1:
            #self._logs.info('Данных ещё не достаточно, функция вызвана впервые, проверку не произвожу')
            print('Данных ещё не достаточно, функция вызвана впервые, проверку не произвожу')
            return False
        else:
            avg_volume = db_local.get_from_db_fetchall(db_local.GET_AVG_VOL)
            print(f'Предстоит спарсить данные по {len(data_for_check[0].index)} тикерам')
            for ticker in data_for_check[0].index:
                try:
                    #self._logs.info(f'Проверяю данные по тикеру {ticker}')
                    print(f'Проверяю данные по тикеру {ticker}')
                    time_of_last_change = pd.Timestamp(data_for_check[0]['time_of_last_change'][data_for_check[0].index == ticker].tolist()[0]).to_pydatetime().replace(second=0).replace(microsecond=0)
                    if (time_now_for_checking - time_of_last_change).seconds > 160:
                        #self._log_warnings.warning(f'Для тикера {ticker} последние данные по свече {time_of_last_change} Время проверки {time_now_for_checking}. Перехожу к следующему инструменту в списке')
                        print(f'Для тикера {ticker} последние данные по свече {time_of_last_change} Время проверки {time_now_for_checking}. Перехожу к следующему инструменту в списке')
                        continue
                    try:
                        print(f'Текущий объём по тикеру {ticker} --- {data_for_check[0].m5_volume[data_for_check[0].index == ticker].tolist()[0]} | Средний объём по тикеру {ticker} --- {avg_volume.avg_m5_volume[avg_volume["ticker"] == ticker].tolist()[0]} | Время свечи - {pd.Timestamp(data_for_check[0]["time_of_last_change"][data_for_check[0].index == ticker].tolist()[0]).to_pydatetime()}')
                        #self._logs.info(f'Текущий объём по тикеру {ticker} --- {data_for_check[0].m5_volume[data_for_check[0].index == ticker].tolist()[0]} | Средний объём по тикеру {ticker} --- {avg_volume.avg_m5_volume[avg_volume["ticker"] == ticker].tolist()[0]} | Время свечи - {pd.Timestamp(data_for_check[0]["time_of_last_change"][data_for_check[0].index == ticker].tolist()[0]).to_pydatetime()}')
                    except Exception as e:
                        #self._log_errors.exception(f'Для тикера {ticker} среднего объёма нет в списке  -- иду дальше', exc_info=e)
                        print(f'Для тикера {ticker} среднего объёма нет в списке  -- иду дальше, {e}')
                        continue
                    try:
                        delta = (data_for_check[0].m5_volume[data_for_check[0].index == ticker].tolist()[0]/avg_volume.avg_m5_volume[avg_volume['ticker'] == ticker].tolist()[0])
                    except Exception as e:
                        #self._log_errors.exception(f'Какая-то ошибка', exc_info=e)
                        print(f'Какая-то ошибка, {e}')
                        continue
                    if delta >= 20:
                        self._log_warnings.warning(f'Найдена аномалия по тикеру -- {ticker}--|--объём выше среднего в {delta} раз, изменения цены от начала дня: {data_for_check[0].chg_price_per[data_for_check[0].index == ticker].tolist()[0]}  |  Изменение цены за последнюю минуту: {data_for_check[0].m5_chg_price_prc[data_for_check[0].index == ticker].tolist()[0]} |  заношу данные в БД')
                        ticker_name = data_for_check[0].ticker_name[data_for_check[0].index == ticker].values[0].replace(' [SPB: Акции]', '')
                        db_global.insert_market_movement_spb(ticker, ticker_name, data_for_check[0].m5_volume[data_for_check[0].index == ticker].tolist()[0], delta, Decimal(avg_volume.avg_m5_volume[avg_volume.ticker == ticker].tolist()[0]).quantize(Decimal("1.00"), ROUND_HALF_EVEN), Decimal(avg_volume.avg_daily_volume[avg_volume.ticker == ticker].tolist()[0]).quantize(Decimal("1.00"), ROUND_HALF_EVEN), data_for_check[0].price_last_deal[data_for_check[0].index == ticker].tolist()[0], data_for_check[0].m5_chg_price_prc[data_for_check[0].index == ticker].tolist()[0], data_for_check[0].chg_price_per[data_for_check[0].index == ticker].tolist()[0], time_now_for_checking - datetime.timedelta(minutes=1))  
                    else:
                        #self._logs.info(f'По тикеру {ticker} аномалий не найдено, иду дальше')
                        print(f'По тикеру {ticker} аномалий не найдено, иду дальше')
                except Exception as e:
                    #self._log_errors.exception(f'Какая-то ошибка', exc_info=e)
                    print(f'Какая-то ошибка, {e}')
                    continue
            return True

updater_spimex = UpdaterSPIMEX()