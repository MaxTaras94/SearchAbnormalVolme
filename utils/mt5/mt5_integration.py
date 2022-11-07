from data.config import LOGINMT5, PASSMT5, SERVERMT5
import datetime
from decimal import Decimal, ROUND_HALF_EVEN
import MetaTrader5 as mt5
import pytz
import time


class MT5Quotes():
    """
    Данный класс создан для получения котировок
    по заданному списку инструментов напрямую
    от брокера AMarkets посредстов подключения к нему через MT5
    """

    def __init__(self):
        self._check_name = {'dashboard_eng':
                                [['S&P500',
                                  'Nasdaq100',
                                  'WTI',
                                  'XAUUSD',
                                  'EURUSD',
                                  'VIX',
                                  'BTCUSD'],
                                 {'S&P500': 'S&P500',
                                  'Nasdaq100': 'NASD100',
                                  'WTI': 'WTI',
                                  'XAUUSD': 'GOLD',
                                  'EURUSD': 'EUR/USD',
                                  'VIX': 'VIX',
                                  'BTCUSD': 'BTC'}],
                            'dashboard_rus':
                                [['RTS',
                                  'S&P500',
                                  'DAX30',
                                  'BRENT',
                                  'USDRUB',
                                  'EURUSD',
                                  'BTCUSD'],
                                 {'RTS': 'RTS',
                                  'S&P500': 'S&P500',
                                  'DAX30': 'DAX',
                                  'BRENT': 'BRENT',
                                  'USDRUB': 'USD/RUB',
                                  'EURUSD': 'EUR/USD',
                                  'BTCUSD': 'BTC'}],
                            'crypto':
                                [['BTCUSD', 'ETHUSD',
                                  'DSHUSD', 'XRPUSD',
                                  'LTCUSD'],
                                 {'BTCUSD': 'BTC',
                                  'ETHUSD': 'ETH',
                                  'DSHUSD': 'DSH',
                                  'XRPUSD': 'XRP',
                                  'LTCUSD': 'LTC'}],
                            'indexes':
                                [['DowJones30',
                                  'S&P500',
                                  'Russell2000',
                                  'Nasdaq100',
                                  'FTSE100',
                                  'CAC40',
                                  'EuroStoxx50',
                                  'IBEX35',
                                  'ITA40',
                                  'DAX30',
                                  'RTS',
                                  'China50',
                                  'Nikkei225',
                                  'ASX200',
                                  'DXY',
                                  'VIX',
                                  'TNOTE',
                                  'BUND10Y'
                                  ],
                                 {'Nasdaq100': 'NASD100',
                                  'Russell2000': 'RSL2000',
                                  'China50': 'CHN50',
                                  'FTSE100': 'FTSE',
                                  'EuroStoxx50': 'EU50',
                                  'IBEX35': 'IBEX35',
                                  'ITA40': 'ITA40',
                                  'Nikkei225': 'NIK225',
                                  'ASX200': 'ASX200',
                                  'CAC40': 'CAC40',
                                  'VIX': 'VIX',
                                  'TNOTE': 'US10Y',
                                  'BUND10Y': 'BUND10Y',
                                  'DowJones30': 'DJIA',
                                  'DXY': 'DXY',
                                  'RTS': 'RTS',
                                  'DAX30': 'DAX',
                                  'S&P500': 'SP500'}],
                            'commodities':
                                [['XAUUSD',
                                  'XAGUSD',
                                  'PLATINUM',
                                  'ALUMINIUM',
                                  'COPPER',
                                   'NICKEL',
                                   'ZINC',
                                   'COFFEE',
                                   'CORN',
                                   'COTTONS',
                                   'SOYBEAN',
                                   'SUGARS',
                                   'WHEAT',
                                   'COCOA',
                                   'EMISS',
                                   'NGAS',
                                  'BRENT',
                                  'WTI'],
                                 {'WTI': 'WTI',
                                  'BRENT': 'BRENT',
                                  'PLATINUM': 'PLAT',
                                  'ALUMINIUM': 'ALUM',
                                  'COPPER': 'COPPER',
                                  'NICKEL': 'NICKEL',
                                  'ZINC': 'ZINC',
                                  'COFFEE': 'COFFEE',
                                  'CORN': 'CORN',
                                  'COTTONS': 'COTTONS',
                                  'SOYBEAN': 'SOYBEAN',
                                  'SUGARS': 'SUGARS',
                                  'WHEAT': 'WHEAT',
                                  'COCOA': 'COCOA',
                                  'EMISS': 'EMISS',
                                  'NGAS': 'NGAS',
                                  'XAGUSD': 'SILVER',
                                  'XAUUSD': 'GOLD'}],
                            'forex':
                                [['EURUSD',
                                  'GBPUSD',
                                   'AUDUSD',
                                   'NZDUSD',
                                   'USDCAD',
                                  'USDCHF',
                                  'USDJPY',
                                   'USDMXN',
                                  'USDTRY',
                                   'USDNOK',
                                   'USDPLN',
                                   'USDSEK',
                                  'USDRUB',
                                  'EURRUB'
                                  ],
                                 {'USDCHF': 'USD/CHF',
                                  'AUDUSD': 'AUD/USD',
                                  'NZDUSD': 'NZD/USD',
                                  'USDCAD': 'USD/CAD',
                                  'GBPUSD': 'GBP/USD',
                                  'USDJPY': 'USD/JPY',
                                  'USDMXN': 'USD/MXN',
                                  'USDTRY': 'USD/TRY',
                                  'USDNOK': 'USD/NOK',
                                  'USDPLN': 'USD/PLN',
                                  'USDSEK': 'USD/SEK',
                                  'EURUSD': 'EUR/USD',
                                  'EURRUB': 'EUR/RUB',
                                  'USDRUB': 'USD/RUB'}]}

        self._excluder = [
                            'CAC40',
                            'EuroStoxx50',
                            'IBEX35',
                            'ITA40',
                            'AUDUSD',
                            'NZDUSD',
                            'USDCAD',
                            'USDMXN',
                            'USDNOK',
                            'USDPLN',
                            'USDSEK',
                            'NICKEL',
                            'ZINC',
                            'COFFEE',
                            'CORN',
                            'COTTONS',
                            'SOYBEAN',
                            'SUGARS',
                            'WHEAT',
                            'COCOA',
                            'EMISS',
                            'NGAS',
                            'China50',
                            'Nikkei225',
                            'ASX200',
                            'Russell2000',
                            'DXY',
                            'TNOTE',
                            'BUND10Y'
                        ]

    def __initialize_terminal(self):
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
        if self.__initialize_terminal():
            st = mt5.login(LOGINMT5, password=PASSMT5, server=SERVERMT5)
            return st

    def _parsing_ticker_info(self, group_type, date) -> dict():
        result = [[], []] #1-й вложенный список наполняется всеми инстурментами, 2-й только теми, которые отсутствуют  в списке self._excluder
        for ticker in self._check_name[group_type][0]:
            try:
                rate_yesterday = Decimal(mt5.copy_rates_from(ticker, mt5.TIMEFRAME_D1, date, 1)['close'][0]).quantize(Decimal("1.0000"), ROUND_HALF_EVEN)
                rate_curr =  Decimal(mt5.symbol_info_tick(ticker)._asdict()['bid']).quantize(Decimal("1.0000"), ROUND_HALF_EVEN)
                chg = Decimal(rate_curr - rate_yesterday).quantize(Decimal("1.0000"), ROUND_HALF_EVEN)
                if ticker not in self._excluder:
                    result[0].append({'group_type':group_type, 'ticker':self._check_name[group_type][1][ticker], 'quote': rate_curr, 'chg': chg, 'chg_percent':Decimal(((rate_curr - rate_yesterday)/rate_yesterday)*100).quantize(Decimal("1.00"), ROUND_HALF_EVEN), 'time': datetime.datetime.today()})
                    result[1].append({'group_type':group_type, 'ticker':self._check_name[group_type][1][ticker], 'quote': rate_curr, 'chg': chg, 'chg_percent':Decimal(((rate_curr - rate_yesterday)/rate_yesterday)*100).quantize(Decimal("1.00"), ROUND_HALF_EVEN), 'time': datetime.datetime.today()})
                else:
                    result[0].append({'group_type':group_type, 'ticker':self._check_name[group_type][1][ticker], 'quote': rate_curr, 'chg': chg, 'chg_percent':Decimal(((rate_curr - rate_yesterday)/rate_yesterday)*100).quantize(Decimal("1.00"), ROUND_HALF_EVEN), 'time': datetime.datetime.today()})
            except:
                print(f'Ошибка в функции _parsing_ticker_info: {mt5.last_error()}')
                result.append({'group_type': group_type,
                               'ticker': self._check_name[group_type][1][ticker],
                               'quote': 0,
                               'chg': 0,
                               'chg_percent': 0,
                               'time': datetime.datetime.today()})
                return result

        return result

    def run(self, group_type) -> dict():
        date = datetime.datetime.today() - datetime.timedelta(days=1)
        utc_from = datetime.datetime(date.year,
                                     date.month,
                                     date.day,
                                     tzinfo=pytz.timezone("Etc/UTC"))
        if self.__log_account_mt5():
            for_channel = self._parsing_ticker_info(group_type, utc_from)
            return for_channel
        else:
            print(f"Ошбика в блоке run: {mt5.last_error()}")
            return for_channel


mt5quotes = MT5Quotes()
