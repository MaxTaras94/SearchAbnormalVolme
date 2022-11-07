# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 21:47:59 2021

@author: TarMS
"""


import datetime
import logging


class Logger():
    
    def __init__(self, name_module, filepath, level):
        self.name_module = name_module
        self.filepath = filepath
        self.level = level
        
    def create_logger(self):  
        self.logger = logging.getLogger(self.name_module)
        level_msg = {'ERROR': logging.ERROR,
                     'DEBUG': logging.DEBUG,
                     'INFO':logging.INFO,
                     'WARNING':logging.WARNING}
        handler = logging.FileHandler(f'{self.filepath}/{self.name_module}_{datetime.datetime.now().strftime("%d.%m.%Y %H-%M")}.log')
        handler.setLevel(level_msg[self.level])
        strfmt = '[%(asctime)s][%(funcName)s][%(levelname)s] >>> %(message)s'
        datefmt = '%d.%m.%Y %H:%M:%S'
        formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        return self.logger
    
        
        