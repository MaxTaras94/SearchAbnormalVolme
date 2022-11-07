# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 21:47:59 2021

@author: TarMS
"""
from data.config import DATA_DIR, SERVER, DBUSERNAME_BACK, DBPASSWORD_BACK, DATABASE, SERVERSPBXM, DBUSERNAMSPBXME, DBPASSWORDSPBXM, DATABASESPBXM
import datetime
from decimal import Decimal, ROUND_HALF_EVEN
import os
import pandas as pd
import pymysql
from utils.Logger import Logger



class DBCommandsGLOBAL:
    """
    Класс для взаимодействия с базой данных MOEX.
    В __init__ прописаны SQL запросы,
    которые ниже реализованы в качестве методов.
    """

    def __init__(self):
        self.__INSERT_MARKET_MOVEMENT_MOEX = "INSERT INTO DataMMMoex (id, ticker, ticker_name, vol_lots, vol_chg, avg_m5_volume, avg_daily_volume, price, price_chg, price_chg_day, candle_time, time) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())"
        self.__INSERT_DIVIDENDS_MOEX = "INSERT INTO DataDividendsMoex (id, ticker, ticker_name, date_expiration, date_close_registry, price, lot, dividends, profitability) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.__INSERT_DIVIDENDS_SPIMEX = "INSERT INTO DataDividendsSpimex (id, ticker, ticker_name, date_expiration, date_close_registry, price, lot, dividends, profitability) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.__UPDATE_DIVIDENDS_MOEX = "INSERT INTO DataDividendsMoex (id, ticker, ticker_name, date_expiration, date_close_registry, price, lot, dividends, profitability) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE price_close = %s, price_open= %s, price_last_deal = %s, count_in_all_deals = %s, previous_day_closing_price = %s, time_of_last_change = %s, time=NOW()"
        self.__INSERT_MARKET_MOVEMENT_SPB = "INSERT INTO DataMMSpb (id, ticker, ticker_name, vol_lots, vol_chg, avg_m5_volume, avg_daily_volume, price, price_chg, price_chg_day, candle_time, time) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())"
        self.__INSERT_MARKET_MOVEMENT_FOREX = "INSERT INTO DataMMForex (id, ticker, ticker_name, vol_lots, vol_chg, avg_m5_volume, avg_daily_volume, price, price_chg, price_chg_day, candle_time, time) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())"
        self.__UPDATE_LEADERS_MOEX = "UPDATE DataLeadersMoex SET ticker = %s, ticker_name = %s, price = %s, price_chg = %s, time = NOW() WHERE id = %s"
        self.__UPDATE_LEADERS_FOREX = "UPDATE DataLeadersForex SET ticker = %s, ticker_name = %s, price = %s, price_chg = %s, time = NOW() WHERE id = %s"
        self.__UPDATE_LEADERS_SPBXM = "UPDATE DataLeadersSpb SET ticker = %s, ticker_name = %s, price = %s, price_chg = %s, time = NOW() WHERE id = %s"
        self.__INSERT_DATA_ECON_CALENDAR_RU = "INSERT INTO DataEconomicCalendarRU (id, time_published, country, importance, news, color, fact, forecast, previous, row, time) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())"
        self.__UPDATE_DATA_ECON_CALENDAR_RU = "UPDATE DataEconomicCalendarRU SET fact = %s, color = %s WHERE id = %s"
        self.__CLEAR_DataEconomicCalendarRU = "DELETE FROM DataEconomicCalendarRU"
        self.__CLEAR_DataDividendsMoex = "DELETE FROM DataDividendsMoex"
        self.__CLEAR_DataDividendsSpimex = "DELETE FROM DataDividendsSpimex"
        self.__INSERT_DATA_ECON_CALENDAR_EN = "INSERT INTO DataEconomicCalendarEN (id, time_published, country, importance, news, color, fact, forecast, previous, row, time) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())"
        self.__UPDATE_DATA_ECON_CALENDAR_EN = "UPDATE DataEconomicCalendarEN SET fact = %s, color=%s WHERE id = %s"
        self.__CLEAR_DataEconomicCalendarEN = "DELETE FROM DataEconomicCalendarEN"
        self.__INSERT_NEWS_RU = "INSERT INTO DataNewsRU (id, resource, title, link, time_publ_art, published, time) VALUES (NULL, %s, %s, %s, %s, %s, NOW())"
        self.__GET_NEWS_RU = "SELECT title FROM DataNewsRU WHERE DATE(time_publ_art) = CURDATE()"
        self.__DATA_FROM_DataEconomicCalendar_RU = "SELECT id, time_published, row, previous FROM DataEconomicCalendarRU where time_published > NOW() and previous != ''"       
        self.__INSERT_NEWS_EN = "INSERT INTO DataNewsEN (id, resource, title, link, time_publ_art, published, time) VALUES (NULL, %s, %s, %s, %s, %s, NOW() - INTERVAL 7 HOUR)"
        self.__GET_NEWS_EN = "SELECT title FROM DataNewsEN WHERE DATE(time_publ_art) = CURDATE()"
        self.__DATA_FROM_DataEconomicCalendar_EN = "SELECT id, time_published, row, previous FROM DataEconomicCalendarEN where previous != ''"
        self._log_errors = Logger('BackDataUpdater', os.path.join(DATA_DIR, 'logs back\\DBGLOBAL\\Errors\\'), 'ERROR').create_logger()
        self._logs = Logger('BackDataUpdater', os.path.join(DATA_DIR, 'logs back\\DBGLOBAL\\INFO\\'), 'DEBUG').create_logger()
        self.conn = self.__initialize()
        
    def __db_create_connection(self):
        return pymysql.connect(
            host=SERVER,
            user=DBUSERNAME_BACK,
            password=DBPASSWORD_BACK,
            db=DATABASE)    
    
    def clear_tableRU(self):
        """Функция отчищает таблицу БД"""
        command = self.__CLEAR_DataEconomicCalendarRU
        self.__run_command(command)
    
    def clear_table_dividends_moex(self):
        """Функция отчищает таблицу DataDividendsMoex"""
        command = self.__CLEAR_DataDividendsMoex
        self.__run_command(command)
    
    def clear_table_dividends_spimex(self):
        """Функция отчищает таблицу DataDividendsMoex"""
        command = self.__CLEAR_DataDividendsSpimex
        self.__run_command(command)
        
    def clear_tableEN(self):
        """Функция отчищает таблицу БД"""
        command = self.__CLEAR_DataEconomicCalendarEN
        self.__run_command(command)
        
    def __run_command(self, command):
        """Функция выполняет команду.
        Запрос к БД передаётся в переменной command"""
        self.conn.ping(reconnect=True)
        conn = self.conn
        cur = conn.cursor()
        cur.execute(command)
        conn.commit()
        conn.close()
        
    def __initialize(self):
        try:
            conn = self.__db_create_connection()
            self._logs.info('DB Hoster has connected')
            return conn
        except Exception as err:
            self._log_errors.exception('Ошибка инициализации БД', exc_info=err)
            pass
    
    def get_from_db_fetchall(self, command):
        self.conn.ping(reconnect=True)
        conn = self.conn
        df = pd.read_sql(command, conn)
        conn.close()
        return df

    def write_to_db(self, command, args):
        self.conn.ping(reconnect=True)
        conn = self.conn
        cur = conn.cursor()
        cur.execute(command, args)
        conn.commit()
        conn.close()

    def insert_market_movement_moex(self, ticker, ticker_name, vol_lots, vol_chg, avg_m5_volume, avg_daily_volume, price, price_chg, price_chg_day, candle_time):
        command = self.__INSERT_MARKET_MOVEMENT_MOEX
        args = ticker, ticker_name, vol_lots, vol_chg, avg_m5_volume, avg_daily_volume, price, price_chg, price_chg_day, candle_time
        print(f'Вызван метод insert_market_movement, переданы аргументы {args}')
        self.write_to_db(command, args)
    
    def insert_data_econom_calendar_ru(self, time_published, country, importance, news, color, fact, forecast, previous, row):
        command = self.__INSERT_DATA_ECON_CALENDAR_RU
        args = time_published, country, importance, news, color, fact, forecast, previous, row
        print(f'Вызван метод insert_data_econom_calendar_ru, переданы аргументы {args}')
        self.write_to_db(command, args)
        
    def insert_dividends_moex(self, ticker, ticker_name, date_expiration, date_close_registry, price, lot, dividends, profitability):
        command = self.__INSERT_DIVIDENDS_MOEX
        args = ticker, ticker_name, date_expiration, date_close_registry, price, lot, dividends, profitability
        print(f'Вызван метод insert_dividends_moex, переданы аргументы {args}')
        self.write_to_db(command, args)
   
    def insert_dividends_spimex(self, ticker, ticker_name, date_expiration, date_close_registry, price, lot, dividends, profitability):
        command = self.__INSERT_DIVIDENDS_SPIMEX
        args = ticker, ticker_name, date_expiration, date_close_registry, price, lot, dividends, profitability
        print(f'Вызван метод insert_dividends_spimex, переданы аргументы {args}')
        self.write_to_db(command, args)
        
    def get_from_econom_calendar_ru(self):
        command = self.__DATA_FROM_DataEconomicCalendar_RU
        data = self.get_from_db_fetchall(command)
        return data
    
    def update_date_econom_calendar_ru(self, fact, color, row_id):
        command = self.__UPDATE_DATA_ECON_CALENDAR_RU
        args = fact, color, int(row_id)
        self.write_to_db(command, args)
    
    def insert_data_econom_calendar_en(self, time_published, country, importance, news, color, fact, forecast, previous, row):
        command = self.__INSERT_DATA_ECON_CALENDAR_EN
        args = time_published, country, importance, news, color, fact, forecast, previous, row
        print(f'Вызван метод insert_data_econom_calendar_en, переданы аргументы {args}')
        self.write_to_db(command, args)
   
    def get_from_econom_calendar_en(self):
        command = self.__DATA_FROM_DataEconomicCalendar_EN
        data = self.get_from_db_fetchall(command)
        return data
    
    def update_date_econom_calendar_en(self, fact, color, row_id):
        command = self.__UPDATE_DATA_ECON_CALENDAR_EN
        args = fact, color, int(row_id)
        self.write_to_db(command, args)
        
    def insert_market_movement_spb(self, ticker, ticker_name, vol_lots, vol_chg, avg_m5_volume, avg_daily_volume, price, price_chg, price_chg_day, candle_time):
        command = self.__INSERT_MARKET_MOVEMENT_SPB
        args = ticker, ticker_name, vol_lots, vol_chg, avg_m5_volume, avg_daily_volume, price, price_chg, price_chg_day, candle_time
        print(f'Вызван метод insert_market_movement, переданы аргументы {args}')
        self.write_to_db(command, args)
    
    def insert_news_ru(self, resource, title, link, time_publ_art, published):
        command = self.__INSERT_NEWS_RU
        args = resource, title, link, time_publ_art, published
        print(f'Вызван метод insert_news_ru, переданы аргументы {args}')
        self.write_to_db(command, args)
    
    def get_news_ru(self):
        command = self.__GET_NEWS_RU
        data = self.get_from_db_fetchall(command)
        return data
    
    def insert_news_en(self, resource, title, link, time_publ_art, published):
        command = self.__INSERT_NEWS_EN
        args = resource, title, link, time_publ_art, published
        print(f'Вызван метод insert_news_en, переданы аргументы {args}')
        self.write_to_db(command, args)
    
    def get_news_en(self):
        command = self.__GET_NEWS_EN
        data = self.get_from_db_fetchall(command)
        return data
        
    def update_market_leaders_moex(self, ticker, ticker_name, price, price_chg, row_id):
        command = self.__UPDATE_LEADERS_MOEX
        args = ticker, ticker_name, price, price_chg, row_id
        self.write_to_db(command, args)
    
    def update_market_leaders_spbxm(self, ticker, ticker_name, price, price_chg, row_id):
        command = self.__UPDATE_LEADERS_SPBXM
        args = ticker, ticker_name, price, price_chg, row_id
        self.write_to_db(command, args)
    
class DBCommandsLOCAL:
    """
    Класс для взаимодействия с базой данных SPIMEX.
    В __init__ прописаны SQL запросы,
    которые ниже реализованы в качестве методов.
    """
    def __init__(self):
        self.__GET_ALL = "SELECT * FROM data_from_spbmx where time_of_last_change != ''"
        self.__GET_TOP_TICKERS = "SELECT stockCode FROM data_from_spbmx order by count_in_all_deals DESC"
        self.__GET_LEADERD_GROWTH = "SELECT (stockCode) as ticker, (full_name_ticker) as ticker_name, (price_last_deal) as price, ((price_last_deal - previous_day_closing_price)/previous_day_closing_price*100) as price_chg FROM data_from_spbmx WHERE price_last_deal > 0 and previous_day_closing_price > 0 order by price_chg DESC limit 10"
        self.__GET_LEADERD_FALL = "SELECT (stockCode) as ticker, (full_name_ticker) as ticker_name, (price_last_deal) as price, ((price_last_deal - previous_day_closing_price)/previous_day_closing_price*100) as price_chg FROM data_from_spbmx WHERE price_last_deal > 0 and previous_day_closing_price > 0 order by price_chg ASC limit 10"
        self.Backup = "INSERT INTO m1_data_from_spbmx (full_name_ticker, stockCode, price_close, price_open, price_last_deal, count_in_all_deals, previous_day_closing_price, time_of_last_change, time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW()) ON DUPLICATE KEY UPDATE price_close = %s, price_open= %s, price_last_deal = %s, count_in_all_deals = %s, previous_day_closing_price = %s, time_of_last_change = %s, time=NOW()"
        self.__DB_BACKUP = "INSERT INTO m1_data_from_spbmx (full_name_ticker, stockCode, price_close, price_open, price_last_deal, count_in_all_deals, previous_day_closing_price, time_of_last_change, time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())"
        self.__CLEAR_TABLE = "TRUNCATE TABLE m1_data_from_spbmx"
        self.__UPDATE_M5_AVG_VOLUME = "UPDATE m5_avg_volume SET ticker = %s, avg_m5_volume = %s, avg_daily_volume = %s where id = %s"
        self.__INSERT_M5_AVG_VOLUME = "INSERT INTO m5_avg_volume (id, ticker, avg_m5_volume, avg_daily_volume) VALUES(%s, %s, %s, %s)"
        self.GET_FROM_DB_BACKUP = "SELECT (stockCode) as ticker, (full_name_ticker) as ticker_name, (count_in_all_deals) as volume, price_last_deal, price_open, ((price_last_deal - previous_day_closing_price)/previous_day_closing_price)*100 as chg_price_per, time_of_last_change FROM m1_data_from_spbmx order by count_in_all_deals"
        self.GET_AVG_VOL = "SELECT * FROM m5_avg_volume WHERE avg_daily_volume >= 10000"
        self._from_spb = pd.DataFrame()
        self._log_errors = Logger('BackDataUpdater', os.path.join(DATA_DIR, 'logs back\\DBLOCAL\\Errors\\'), 'ERROR').create_logger()
        self._logs = Logger('BackDataUpdater', os.path.join(DATA_DIR, 'logs back\\DBLOCAL\\INFO\\'), 'DEBUG').create_logger()
        self.conn = self.__initialize()
        
    def __db_create_connection(self):
        """Подключения к БД"""
        return pymysql.connect(
            host=SERVERSPBXM,
            user=DBUSERNAMSPBXME,
            password=DBPASSWORDSPBXM,
            db=DATABASESPBXM)    
    
    def __initialize(self):
        """Инициализация подключения к БД"""
        try:
            conn = self.__db_create_connection()
            self._logs.info('DB localhost has connected')
            return conn
        except Exception as err:
            self._log_errors.exception('Ошибка инициализации БД', exc_info=err)
            pass
                 
    def get_from_db_fetchall(self, command):
        """Функция возвращает все записи в БД.
        Запрос к БД передаётся в переменной command"""
        self.conn.ping(reconnect=True)
        conn = self.conn
        df = pd.read_sql(command, conn)
        return df
    
    def __write_to_db(self, conn, command, args):
        """Функция записыавет переданные в неё данные в БД.
        Запрос к БД передаётся в переменной command
        Данные для записи передаются в переменной args"""
        cur = conn.cursor()
        cur.execute(command, args)
    
    def __run_command(self, command):
        """Функция выполняет команду.
        Запрос к БД передаётся в переменной command"""
        self.conn.ping(reconnect=True)
        conn = self.conn
        cur = conn.cursor()
        cur.execute(command)
        conn.commit()
        conn.close()
        
    def get_all_data(self, command):
        """Функция возвращает все записи в БД."""
        data = self.get_from_db_fetchall(command)
        return data
    
    def get_top_tickers(self):
        """Функция возвращает ТОП акций Питерской биржи, отсортированных по обороту выше 10 000 лотов"""
        command = self.__GET_TOP_TICKERS
        data = self.get_from_db_fetchall(command)
        return [ticker+"_SPB" for ticker in data.stockCode.to_list()]
    
    def get_leaders_growth(self):
        """Функция возвращает ТОП акций Питерской биржи, отсортированных по обороту выше 10 000 лотов и выстроинных по убыванию от акций, показывающий максимальный % роста за день"""
        command = self.__GET_LEADERD_GROWTH
        data = self.get_from_db_fetchall(command)
        data['ticker_name'] = data['ticker_name'].str.replace(' \[SPB: Акции\]', '')
        return data
    
    def get_leaders_fall(self):
        """Функция возвращает ТОП акций Питерской биржи, отсортированных по обороту выше 10 000 лотов и выстроинных по убыванию от акций, показывающий максимальный % падение за день"""
        command = self.__GET_LEADERD_FALL
        data = self.get_from_db_fetchall(command)
        data['ticker_name'] = data['ticker_name'].str.replace(' \[SPB: Акции\]', '')
        return data
    
    def get_leaders(self):
        """Функция собриает лидеров роста и падения и возвращает общий фрейм данных"""
        total = pd.DataFrame(self.get_leaders_growth())     
        total = total.append(self.get_leaders_fall())
        return total
    
    def __db_truncate_table(self):
        """Функция отчищает таблицу БД"""
        command = self.__CLEAR_TABLE
        self.__run_command(command)
    
    def db_backup (self):
        """Функция делает бэкап БД"""
        command = self.Backup
        data_for_backup = self.get_all_data(self.__GET_ALL)
        date = datetime.datetime.today().replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)
        self.conn.ping(reconnect=True)
        conn = self.conn
        for row in range(len(data_for_backup)):
            time_of_last_change = pd.to_datetime(pd.Timestamp('today').normalize() + data_for_backup.time_of_last_change[row])
            args = data_for_backup.full_name_ticker[row], data_for_backup.stockCode[row], Decimal(float(data_for_backup.price_close[row])), Decimal(float(data_for_backup.price_open[row])), Decimal(float(data_for_backup.price_last_deal[row])), int(data_for_backup.count_in_all_deals[row]), Decimal(float(data_for_backup.previous_day_closing_price[row])), time_of_last_change, Decimal(float(data_for_backup.price_close[row])), Decimal(float(data_for_backup.price_open[row])), Decimal(float(data_for_backup.price_last_deal[row])), int(data_for_backup.count_in_all_deals[row]), Decimal(float(data_for_backup.previous_day_closing_price[row])), time_of_last_change
            self.__write_to_db(conn, command, args)
        conn.commit()
        conn.close()
        return True
    
        
    def update_avg_m5_volume(self, data):
        """Функция обновляет данные по среднему объёму 5-ти мин свечей"""
        command = self.__UPDATE_M5_AVG_VOLUME
        self.conn.ping(reconnect=True)
        conn = self.conn 
        for row in range(len(data)):
            args = data['ticker'][row], Decimal(data['avg_m5_volume'][row]), Decimal(data['avg_daily_volume'][row]), row
            self.__write_to_db(conn, command, args)
        conn.commit()
        conn.close()
        
    
    def insert_avg_m5_volume(self, data):
        """Функция добавляет в БД данные по среднему объёму 5-ти мин свечей"""
        command = self.__INSERT_M5_AVG_VOLUME
        self.conn.ping(reconnect=True)
        conn = self.conn
        for row in range(len(data)):
            args = int(data.index[row]), data['ticker'][row], Decimal(data['avg_m5_volume'][row]), Decimal(data['avg_daily_volume'][row])
            self.__write_to_db(conn, command, args)
        conn.commit()
        conn.close()


db_global = DBCommandsGLOBAL()
db_local = DBCommandsLOCAL()
