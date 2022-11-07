# -*- coding: utf-8 -*-
"""
Модуль для запуска цикла по поиску аномальных объёмов
"""



import asyncio
import datetime
import time
# from utils.Logger import Logger
from utils.CheckMarketVolume import updater_forex



class ForexUpdater():
    
    '''Класс запускает цикл бесконечного 
    поиска аномальных всплесков объёма на Forex'''
    
    def __init__(self):
        self.run = asyncio.create_task(self.start())
        self.check_name = updater_forex.check_name
    
    async def start(self):
        finished = False
        while not finished:
            try:
                await self.sleeping_for_update()
                await updater_forex.checking_for_abnormal_volume_forex()                
            except Exception as e:
                print(f'Ошибка -- {e}')              
        
    async def sleeping_for_update(self):
        time_now = datetime.datetime.today()
        #delta = 5
        delta = (4 - time_now.minute % 5) * 60 + (65 - time_now.second) #65 здесь для того, чтобы дать задержку к началу цикла в 5 сек.
        c = 0
        start_time = time.time()
        while c<delta:
            await asyncio.sleep(0.04)
            c += 0.04
            print(f'До старта цикла: {"{:>.0f}".format(delta- (time.time() - start_time))} сек.', end="\r")
            if delta-(time.time()-start_time) < 0.1:
                break

        
if __name__ == "__main__": 
    # logs = Logger('Main', 'logs back/MAIN/Info/', 'DEBUG').create_logger()
    # logs.info('Запустился модуль ForexdataUpdater')
    while True:
        try:
            forex_updater = ForexUpdater()   
        except Exception as e:
            # log_errors = Logger('Main', 'logs back/MAIN/Errors/', 'ERROR').create_logger()
            # log_errors.exception('Ошибка в модуле', exc_info=e)
            print(f'Ошибка в модуле -- {e}')
    