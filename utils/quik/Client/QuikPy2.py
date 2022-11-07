# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 10:34:16 2021

@author: TarMS
"""

import socket  # Обращаться к LUA скриптам QuikSharp будем через соединения
import threading  # Результат работы функций обратного вызова будем получать в отдельном потоке
import json  # Передавать и принимать данные в QUIK будем через JSON


class SingletonQP(type):
    """Метакласс для создания Singleton классов"""
    def __init__(cls, *args, **kwargs):
        """Инициализация класса"""
        super(SingletonQP, cls).__init__(*args, **kwargs)
        cls._singletonqp = None  # Экземпляра класса еще нет

    def __call__(cls, *args, **kwargs):
        """Вызов класса"""
        if cls._singletonqp is None:  # Если класса нет в экземплярах класса
            cls._singletonqp  = super(SingletonQP, cls).__call__(*args, **kwargs)
        return cls._singletonqp  # Возвращаем экземпляр класса


class QuikPy(metaclass=SingletonQP):  # Singleton класс
    """Работа с Quik из Python через LUA скрипты QuikSharp https://github.com/finsight/QUIKSharp/tree/master/src/QuikSharp/lua
     На основе Документации по языку LUA в QUIK из https://arqatech.com/ru/support/files/
     """
    __bufferSize = 1048576  # Размер буфера приема в байтах (1 МБайт)
    __socketRequests = None  # Соединение для запросов
    __callbackThread = None  # Поток обработки функций обратного вызова
    
   
    # Инициализация и вход

    def __init__(self, Host='127.0.0.1', RequestsPort=34130, CallbacksPort=34131):
        """Инициализация"""
        # 2.2. Функции обратного вызова
        self.OnStop = self.DefaultHandler  # 1. Остановка LUA скрипта в терминале QUIK / закрытие терминала QUIK
        self.Host = Host  # 2. IP адрес или название хоста
        self.OnNewCandle = self.DefaultHandler # 3. Получение новой свечки
        self.RequestsPort = RequestsPort  # 4. Порт для отправки запросов и получения ответов
        self.CallbacksPort = CallbacksPort  # 5.  Порт для функций обратного вызова
        self.__socketRequests = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 6. Создаем соединение для запросов
        self.__socketRequests.connect((self.Host, self.RequestsPort))  # 7. Открываем соединение для запросов

        self.__callbackThread = threading.Thread(target=self.CallbackHandler, name='CallbackThread')  # 8. Создаем поток обработки функций обратного вызова
        self.__callbackThread.start()  # 9.  Запускаем поток

    def DefaultHandler(self, data):
        """Пустой обработчик события по умолчанию. Его можно заменить на пользовательский"""
        pass

    def CallbackHandler(self):
        """Поток обработки результатов функций обратного вызова"""
        socketCallbacks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Соединение для функций обратного вызова
        socketCallbacks.connect((self.Host, self.CallbacksPort))  # Открываем соединение для функций обратного вызова
        currentThread = threading.currentThread()  # Получаем текущий поток
        fragments = []  # Будем получать ответ в виде списка фрагментов. Они могут быть разной длины. Ответ может состоять из нескольких фрагментов
        while getattr(currentThread, 'process', True):  # Пока поток нужен
            while True:  # Пока есть что-то в буфере ответов
                fragment = socketCallbacks.recv(self.__bufferSize)  # Читаем фрагмент из буфера
                fragments.append(fragment.decode('cp1251'))  # Переводим фрагмент в Windows кодировку 1251, добавляем в список
                if len(fragment) < self.__bufferSize:  # Если в принятом фрагменте данных меньше чем размер буфера
                    break  # то, возможно, это был последний фрагмент, выходим из чтения буфера
            data = ''.join(fragments)  # Собираем список фрагментов в строку
            dataList = data.split('\n')  # Одновременно могут прийти несколько функций обратного вызова, разбираем их по одной
            fragments = []  # Сбрасываем фрагменты. Если последнюю строку не сможем разобрать, то занесем ее сюда
            for data in dataList:  # Пробегаемся по всем функциям обратного вызова
                if data == '':  # Если функция обратного вызова пустая
                    continue  # то ее не разбираем, переходим на следующую функцию, дальше не продолжаем
                try:  # Пробуем разобрать функцию обратного вызова
                    data = json.loads(data)  # Возвращаем полученный ответ в формате JSON
                except json.decoder.JSONDecodeError:  # Если разобрать не смогли (пришла не вся строка)
                    fragments.append(data)  # то, что не разобрали ставим в список фрагментов
                    break  # т.к. неполной может быть только последняя строка, то выходим из разбора функций обратного выходва

                if data['cmd'] == 'OnDisconnected':  # 20. Отключение терминала от сервера QUIK
                    self.OnDisconnected(data)
                elif data['cmd'] == 'OnConnected':  # 21. Соединение терминала с сервером QUIK
                    self.OnConnected(data)
                # OnCleanUp - 22. Смена сервера QUIK / Пользователя / Сессии
                elif data['cmd'] == 'OnClose':  # 23. Закрытие терминала QUIK
                    self.OnClose(data)
                elif data['cmd'] == 'OnStop':  # 24. Остановка LUA скрипта в терминале QUIK / закрытие терминала QUIK
                    self.OnStop(data)
                elif data['cmd'] == 'OnInit':  # 25. Запуск LUA скрипта в терминале QUIK
                    self.OnInit(data)
                # Разбираем функции обратного вызова QuikSharp
                elif data['cmd'] == 'NewCandle':  # Получение новой свечки
                    self.OnNewCandle(data)
                elif data['cmd'] == 'OnError':  # Получено сообщение об ошибке
                    self.OnError(data)
        socketCallbacks.close()  # Закрываем соединение для ответов

    def ProcessRequest(self, Request):
        """Отправляем запрос в QUIK, получаем ответ из QUIK"""
        rawData = json.dumps(Request)  # Переводим запрос в формат JSON
        self.__socketRequests.sendall(f'{rawData}\r\n'.encode())  # Отправляем запрос в QUIK
        fragments = []  # Гораздо быстрее получать ответ в виде списка фрагментов
        while True:  # Пока фрагменты есть в буфере
            fragment = self.__socketRequests.recv(self.__bufferSize)  # Читаем фрагмент из буфера
            fragments.append(fragment.decode('cp1251'))  # Переводим фрагмент в Windows кодировку 1251, добавляем в список
            if len(fragment) < self.__bufferSize:  # Если в принятом фрагменте данных меньше чем размер буфера
                data = ''.join(fragments)  # Собираем список фрагментов в строку
                try:  # Бывает ситуация, когда данных приходит меньше, но это еще не конец данных
                    return json.loads(data)  # Попробуем вернуть ответ в формате JSON в Windows кодировке 1251
                except json.decoder.JSONDecodeError:  # Если это еще не конец данных
                    pass  # то ждем фрагментов в буфере дальше


    def __enter__(self):
        """Вход в класс, например, с with"""
        return self

    # Фукнции связи с QuikSharp
    
    def Ping(self, TransId=0):
        """Проверка соединения. Отправка ping. Получение pong"""
        return self.ProcessRequest({'data': 'Ping', 'id': TransId, 'cmd': 'ping', 't': ''})

    def Echo(self, Message, TransId=0):
        """Эхо. Отправка и получение одного и того же сообщения"""
        return self.ProcessRequest({'data': Message, 'id': TransId, 'cmd': 'echo', 't': ''})

    def DivideStringByZero(self, TransId=0):
        """Тест обработки ошибок. Выполняется деление на 0 с выдачей ошибки"""
        return self.ProcessRequest({'data': '', 'id': TransId, 'cmd': 'divide_string_by_zero', 't': ''})

    def IsQuik(self, TransId=0):
        """Скрипт запущен в Квике"""
        return self.ProcessRequest({'data': '', 'id': TransId, 'cmd': 'is_quik', 't': ''})

    # 2.1 Сервисные функции

    def IsConnected(self, TransId=0):  # 1
        """Состояние подключения терминала к серверу QUIK. Возвращает 1 - подключено / 0 - не подключено"""
        return self.ProcessRequest({'data': '', 'id': TransId, 'cmd': 'isConnected', 't': ''})

    def GetScriptPath(self, TransId=0):  # 2
        """Путь скрипта без завершающего обратного слэша"""
        return self.ProcessRequest({'data': '', 'id': TransId, 'cmd': 'getScriptPath', 't': ''})

    def GetInfoParam(self, Params, TransId=0):  # 3
        """Значения параметров информационного окна"""
        return self.ProcessRequest({'data': Params, 'id': TransId, 'cmd': 'getInfoParam', 't': ''})

    # message - 4. Сообщение в терминале QUIK. Реализовано в виде 3-х отдельных функций в QuikSharp

    def Sleep(self, Time, TransId=0):  # 5
        """Приостановка скрипта. Время в миллисекундах"""
        return self.ProcessRequest({'data': Time, 'id': TransId, 'cmd': 'sleep', 't': ''})

    def GetWorkingFolder(self, TransId=0):  # 6
        """Путь к info.exe, исполняющего скрипт без завершающего обратного слэша"""
        return self.ProcessRequest({'data': '', 'id': TransId, 'cmd': 'getWorkingFolder', 't': ''})

    def PrintDbgStr(self, Message, TransId=0):  # 7
        """Вывод отладочной информации. Можно посмотреть с помощью DebugView"""
        return self.ProcessRequest({'data': Message, 'id': TransId, 'cmd': 'PrintDbgStr', 't': ''})

    # sysdate - 8. Системные дата и время
    # isDarkTheme - 9. Тема оформления. true - тёмная, false - светлая

    # Сервисные функции QuikSharp
    
    def MessageInfo(self, Message, TransId=0):  # В QUIK LUA message icon_type=1
        """Отправка информационного сообщения в терминал QUIK"""
        return self.ProcessRequest({'data': Message, 'id': TransId, 'cmd': 'message', 't': ''})

    def MessageWarning(self, Message, TransId=0):  # В QUIK LUA message icon_type=2
        """Отправка сообщения с предупреждением в терминал QUIK"""
        return self.ProcessRequest({'data': Message, 'id': TransId, 'cmd': 'warning_message', 't': ''})

    def MessageError(self, Message, TransId=0):  # В QUIK LUA message icon_type=3
        """Отправка сообщения об ошибке в терминал QUIK"""
        return self.ProcessRequest({'data': Message, 'id': TransId, 'cmd': 'error_message', 't': ''})

    # 3.7 Функция для получения информации по инструменту

    def GetSecurityInfo(self, ClassCode, SecCode, TransId=0):  # 1
        """Информация по инструменту"""
        return self.ProcessRequest({'data': f'{ClassCode}|{SecCode}', 'id': TransId, 'cmd': 'getSecurityInfo', 't': ''})

    # Функция для получения информации по инструменту QuikSharp

    def GetSecurityInfoBulk(self, ClassCodes, SecCodes, TransId=0):
        """Информация по инструментам"""
        return self.ProcessRequest({'data': f'{ClassCodes}|{SecCodes}', 'id': TransId, 'cmd': 'getSecurityInfoBulk', 't': ''})

    def GetSecurityClass(self, ClassesList, SecCode, TransId=0):
        """Класс по коду инструмента из заданных классов"""
        return self.ProcessRequest({'data': f'{ClassesList}|{SecCode}', 'id': TransId, 'cmd': 'getSecurityClass', 't': ''})

    # 3.8 Функция для получения даты торговой сессии

    # getTradeDate - 1. Дата текущей торговой сессии

    # 3.9 Функция для получения стакана по указанному классу и инструменту

    def GetQuoteLevel2(self, ClassCode, SecCode, TransId=0):  # 1
        """Стакан по классу и инструменту"""
        return self.ProcessRequest({'data': f'{ClassCode}|{SecCode}', 'id': TransId, 'cmd': 'GetQuoteLevel2', 't': ''})

    # 3.10 Функции для работы с графиками


    # getCandlesByIndex - 3. Информация о свечках (реализовано в get_candles)
    # CreateDataSource - 4. Создание источника данных c функциями: (реализовано в get_candles_from_data_source)
    # - SetUpdateCallback - Привязка функции обратного вызова на изменение свечи
    # - O, H, L, C, V, T - Функции получения цен, объемов и времени
    # - Size - Функция кол-ва свечек в источнике данных
    # - Close - Функция закрытия источника данных. Терминал прекращает получать данные с сервера
    # - SetEmptyCallback - Функция сброса функции обратного вызова на изменение свечи

    # Функции для работы с графиками QuikSharp

    def GetCandlesFromDataSource(self, ClassCode, SecCode, Interval, Count):  # ichechet - Добавлен выход по таймауту
        """Свечки"""
        return self.ProcessRequest({'data': f'{ClassCode}|{SecCode}|{Interval}|{Count}', 'id': '1', 'cmd': 'get_candles_from_data_source', 't': ''})

    def SubscribeToCandles(self, ClassCode, SecCode, Interval, TransId=0):
        """Подписка на свечки"""
        return self.ProcessRequest({'data': f'{ClassCode}|{SecCode}|{Interval}', 'id': TransId, 'cmd': 'subscribe_to_candles', 't': ''})

    def IsSubscribed(self, ClassCode, SecCode, Interval, TransId=0):
        """Есть ли подписка на свечки"""
        return self.ProcessRequest({'data': f'{ClassCode}|{SecCode}|{Interval}', 'id': TransId, 'cmd': 'is_subscribed', 't': ''})

    def UnsubscribeFromCandles(self, ClassCode, SecCode, Interval, TransId=0):
        """Отмена подписки на свечки"""
        return self.ProcessRequest({'data': f'{ClassCode}|{SecCode}|{Interval}', 'id': TransId, 'cmd': 'unsubscribe_from_candles', 't': ''})

    # Выход и закрытие

    def CloseConnectionAndThread(self):
        """Закрытие соединения для запросов и потока обработки функций обратного вызова"""
        self.__socketRequests.close()  # Закрываем соединение для запросов
        self.__callbackThread.process = False  # Поток обработки функций обратного вызова больше не нужен

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из класса, например, с with"""
        self.CloseConnectionAndThread()  # Закрываем соединение для запросов и поток обработки функций обратного вызова

    def __del__(self):
        self.CloseConnectionAndThread()  # Закрываем соединение для запросов и поток обработки функций обратного вызова