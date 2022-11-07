# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 21:47:59 2021

@author: TarMS
"""

import datetime
from decimal import Decimal, ROUND_HALF_EVEN
from utils.db_api.db_commands_back import db_global, db_local
from utils.Logger import Logger


class UpdaterLeaders():
    """
    Данный класс создан для обновления лидеров роста и падения на Московской и Питерской биржах
    """
    
    def __init__(self):
        self._log_errors = Logger('UpdaterLeaders', 'logs back/Leaders/Errors/', 'ERROR').create_logger()
        self._log_warnings = Logger('UpdaterLeaders', 'logs back/Leaders/Warnings/', 'WARNING').create_logger()
        self._logs = Logger('UpdaterLeaders', 'logs back/Leaders/Info/', 'DEBUG').create_logger()
        self._logs.info('UpdaterLeaders запустился')
     
    def db_insert_leaders(self, growth_leaders, fall_leaders):
        self._logs.info('Записываю лидеров')
        try:
            leaders_moex = self._get_leaders_list(growth_leaders, fall_leaders)
            leaders_spbxm = db_local.get_leaders()
            leaders_spbxm.reset_index(inplace=True)
            if len(leaders_moex) == 0:
                self._log_warnings.info(f'Лидеры по Москве - {leaders_moex}')
            else:
                for row_id, leader in enumerate(leaders_moex):
                    db_global.update_market_leaders_moex(leader[0], leader[1][2], Decimal(leader[1][1]).quantize(Decimal("1.0000"), ROUND_HALF_EVEN), Decimal(leader[1][0]).quantize(Decimal("1.00"), ROUND_HALF_EVEN), row_id+1)
            for row in range(len(leaders_spbxm)):
                db_global.update_market_leaders_spbxm(leaders_spbxm.ticker[row], leaders_spbxm.ticker_name[row], Decimal(leaders_spbxm.price[row]).quantize(Decimal("1.0000"), ROUND_HALF_EVEN), Decimal(leaders_spbxm.price_chg[row]).quantize(Decimal("1.00"), ROUND_HALF_EVEN), row+1)      
        except Exception as e:
            self._log_errors.exception('Ошибка в блоке db_insert_leaders', exc_info=e)
    
    def _to_list(self, dct):
        try:
            list_leaders = []
            for key,value in dct.items():
                list_leaders.append([key,value])
        except Exception as e:
            self._log_errors.exception('Ошибка в блоке _to_list', exc_info=e)
        return list_leaders
    
    def _get_leaders_list(self, growth_leaders, fall_leaders):
        try:
            growth_leaders_tuples = sorted(growth_leaders.items(), key=lambda item: item[1], reverse=True)
            growth_leaders = {k: v for k, v in growth_leaders_tuples[:10]}
            fall_leaders_tuples = sorted(fall_leaders.items(), key=lambda item: item[1])
            fall_leaders = {k: v for k, v in fall_leaders_tuples[:10]}
            if len(growth_leaders) < 10 and len(fall_leaders) == 10:
                delta_fall = 10 - len(growth_leaders)
                fall_leaders = {k: v for k, v in fall_leaders_tuples[:10+delta_fall]}
            elif len(growth_leaders) == 10 and len(fall_leaders) < 10:
                delta_growth = 10 - len(fall_leaders)
                growth_leaders = {k: v for k, v in growth_leaders_tuples[:10+delta_growth]}
            elif len(growth_leaders) < 10 and len(fall_leaders) < 10:
                return []
            else:
                pass
            growth_leaders.update(fall_leaders)
            list_leaders = self._to_list(growth_leaders)
        except Exception as e:
            self._log_errors.exception('Ошибка в блоке _get_leaders_list', exc_info=e)
        return list_leaders

updater_leaders = UpdaterLeaders()