# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 16:22:35 2021

@author: TarMS
"""
import datetime
import pandas as pd
from QuikPy2 import QuikPy  # Работа с Quik из Python через LUA скрипты QuikSharp
import time



class SingletonGMM(type):
    """Метакласс для создания Singleton классов"""
    def __init__(cls, *args, **kwargs):
        """Инициализация класса"""
        super(SingletonGMM, cls).__init__(*args, **kwargs)
        cls._singletongmm = None  # Экземпляра класса еще нет

    def __call__(cls, *args, **kwargs):
        """Вызов класса"""
        if cls._singletongmm is None:  # Если класса нет в экземплярах класса
            cls._singletongmm  = super(SingletonGMM, cls).__call__(*args, **kwargs)
        else:
            print('Вызвак метод __call__ класса SingletonGMM')
        return cls._singletongmm  # Возвращаем экземпляр класса

def PrintCallback1(data):
    """Пользовательский обработчик событий:
    - Изменение стакана котировок
    - Получение обезличенной сделки
    - Получение новой свечки
    """
    print(data['data'])  # Печатаем полученные данн
    
class GetMarkerMovements():
    """
    Класс для получения обновлений по рыночным аномалиям заданного списка бумаг Мск и Спб бирж
    """
    
    __file = pd.read_excel(r'C:\Users\TarMS\Documents\Python Scripts\Parsing_MICEX.xlsx')
    
    def __init__(self):
        self.qpProvider = QuikPy()
   
    
    def PrintCallback(self, data):
        """Пользовательский обработчик событий:
        - Изменение стакана котировок
        - Получение обезличенной сделки
        - Получение новой свечки
        """
        
        print(data['data'])  # Печатаем полученные данные
        

    def test(self, data):
        qpProvider.OnNewCandle = PrintCallback1
        qpProvider.SubscribeToCandles(__file.Code_class[num], __file.Code_stock[num], 5, 0)
        qpProvider.SubscribeToCandles(__file.Code_class[1], __file.Code_stock[1], 5, 1)