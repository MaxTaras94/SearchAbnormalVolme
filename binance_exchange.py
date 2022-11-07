from binance.spot import Spot
from data.config import api_key, secret_key
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_EVEN
import pandas as pd

class Binance():

    def __init__(self):
        self._client = Spot(key=api_key, secret=secret_key)
        print(f"Время сервера: {pd.to_datetime(self._client.time()['serverTime'], unit='ms')+ timedelta(hours=3)}")
        self.all_symbols = [s['symbol'] for s in self._client.exchange_info()['symbols']]
    
    def parse_response_for_last_candle(self):
        '''Конвертирование ответа из списка в словарь'''
        self.last_candle_dict = {'Open time': pd.to_datetime(self.last_candle[0], unit='ms') + timedelta(hours=3),
                                 'Open': self.last_candle[1],
                                 'High': self.last_candle[2],
                                 'Low': self.last_candle[3],
                                 'Close': self.last_candle[4],
                                 'Vol(BTC)': '{0:,}'.format(Decimal(float(self.last_candle[5])).quantize(Decimal("1.00"), ROUND_HALF_EVEN)).replace(',', ' '),
                                 'Vol(USDT)': '{0:,}'.format(Decimal(float(self.last_candle[7])).quantize(Decimal("1.00"), ROUND_HALF_EVEN)).replace(',', ' '),
                                 'Close time': pd.to_datetime(self.last_candle[6], unit='ms') + timedelta(hours=3),
                                 'Number of trades': self.last_candle[8],
                                 'Taker buy base asset volume': self.last_candle[9],
                                 'Taker buy quote asset volume': self.last_candle[10]}
        print(self.last_candle_dict)
    
    def parse_response_for_many_candles(self):
        '''Конвертирование ответа из списка в словарь'''
        self.many_candles_dict = []
        for candle in self.many_candles:
            self.many_candles_dict.append({'Open time': pd.to_datetime(candle[0], unit='ms') + timedelta(hours=3),
                                     'Open': candle[1],
                                     'High': candle[2],
                                     'Low': candle[3],
                                     'Close': candle[4],
                                     'Vol(BTC)': '{0:,}'.format(Decimal(float(candle[5])).quantize(Decimal("1.00"), ROUND_HALF_EVEN)).replace(',', ' '),
                                     'Vol(USDT)': '{0:,}'.format(Decimal(float(candle[7])).quantize(Decimal("1.00"), ROUND_HALF_EVEN)).replace(',', ' '),
                                     'Close time': pd.to_datetime(candle[6], unit='ms') + timedelta(hours=3),
                                     'Number of trades': candle[8],
                                     'Taker buy base asset volume': candle[9],
                                     'Taker buy quote asset volume': candle[10]})
        self.df = pd.DataFrame(self.many_candles_dict)
       #self.df.to_excel(r'C:\Users\dnevn\OneDrive\Документы\btc.xlsx')

        
        
        print(self.df)
        
        
    def get_one_candle(self, pair):
        '''Получение последней 5-ти минутной свечи по заданному инструменту'''
        self.last_candle = self._client.klines(pair, '5m', limit=2)[0]
        self.parse_response_for_last_candle()
        
    
    def get_many_candle(self, pair):
        '''Получение данных по 10 тыс. 5-ти минутных свечей для заданного инструмента'''
        dt_from_milli = int(round((datetime.now() - timedelta(days=30)).timestamp() * 1000))
        dt_to_milli = int(round((datetime.now()).timestamp() * 1000))
        self.many_candles = self._client.klines(pair, '5m', startTime=dt_from_milli, endTime=dt_to_milli, limit=1000)
        self.parse_response_for_many_candles()
        df_total = pd.DataFrame([], columns=self.df.columns)
        df_total=df_total.append(self.df)
        while not (datetime.now() - self.df.iloc[-1]['Open time']).days == 0:
            dt_from_milli = int(round((self.df.iloc[-1]['Open time']).timestamp() * 1000))
            self.many_candles = self._client.klines(pair, '5m', startTime=dt_from_milli, endTime=dt_to_milli, limit=1000)
            self.parse_response_for_many_candles()
            df_total=df_total.append(self.df)
            print(df_total)
        df_total.to_excel(r'C:\Users\dnevn\OneDrive\Документы\btc_total.xlsx')
            
if __name__ == '__main__':
    binance_exchange = Binance()
    binance_exchange.get_many_candle('BTCUSDT')