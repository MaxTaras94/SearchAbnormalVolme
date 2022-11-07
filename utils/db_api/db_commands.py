import logging
import aiomysql
from aiogram import types
from loader import db
import datetime


class DBCommands:
    """
    Класс для взаимодействия с базой данных.
    В __init__ прописаны SQL запросы,
    которые ниже реализованы в качестве методов.
    """

    def __init__(self):
        self.ADD_NEW_USER = "INSERT INTO BotUsers (id, chat_id, username, first_name, last_name, lang, reg_time) VALUES (NULL, %s, %s, %s, %s, %s, NOW())"
        self.UPDATE_USER_LANG = "UPDATE BotUsers SET lang = %s WHERE chat_id = %s"
        self.INSERT_NEWSUBSCRIBE = "INSERT INTO BotUsersSubscribes (id, chat_id, subscribe_channel_id, subscribe_channel, subscribe_period, subscribe_price, subscribe_status, payment_status, payment_amount, payment_currency, provider_payment_charge_id, channel_link, start_time, paid_till, last_notify_time, reg_time) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.UPDATE_NEWSUBSCRIBE = "UPDATE BotUsersSubscribes SET subscribe_status = %s, payment_status = %s, provider_payment_charge_id = %s, channel_link = %s, start_time = %s, paid_till = %s WHERE chat_id = %s AND reg_time = %s"
        self.UPDATE_SUBSCRIBE = "UPDATE BotUsersSubscribes SET provider_payment_charge_id = %s, channel_link = %s, paid_till = %s WHERE id = %s"
        self.GET_USER_SUBSCRIBES = "SELECT * FROM BotUsersSubscribes WHERE chat_id = %s AND paid_till >= NOW() ORDER BY id ASC"
        self.GET_USER_SUBSCRIBE = "SELECT * FROM BotUsersSubscribes WHERE subscribe_channel_id = %s AND chat_id = %s AND paid_till >= NOW() ORDER BY id ASC"
        self.GET_USERS_ACTIVE_SUBSCRIBES = "SELECT * FROM BotUsersSubscribes WHERE subscribe_status = %s ORDER BY id ASC"
        self.UPDATE_USER_SUBSCRIBE_STATUS = "UPDATE BotUsersSubscribes SET subscribe_status = %s WHERE chat_id = %s AND subscribe_channel_id = %s AND subscribe_status = %s"
        self.UPDATE_USER_SUBSCRIBE_LAST_NOTIFY_TIME = "UPDATE BotUsersSubscribes SET last_notify_time = %s WHERE id = %s"

        self.GET_LAST_MARKET_MOVEMENTS_MOEX_SPB = "SELECT * FROM DataMMMoex WHERE time >= SUBTIME (NOW(), '00:01:00') AND (vol_chg >= 100 OR price_chg >= 3 OR price_chg <= -3) UNION SELECT * FROM DataMMSpb WHERE time >= SUBTIME (NOW(), '00:01:00') AND (vol_chg >= 100 OR price_chg >= 3 OR price_chg <= -3) UNION SELECT * FROM DataMMForex WHERE time >= SUBTIME (NOW(), '00:01:00') AND (vol_chg >= 100 OR price_chg >= 3 OR price_chg <= -3) ORDER BY vol_chg * avg_daily_volume DESC LIMIT %s"
        self.GET_LAST_MARKET_MOVEMENTS_SPB = "SELECT * FROM DataMMSpb WHERE time >= SUBTIME (NOW(), '00:01:00') AND (vol_chg >= 100 OR price_chg >= 3 OR price_chg <= -3) UNION SELECT * FROM DataMMForex WHERE time >= SUBTIME (NOW(), '00:01:00') AND (vol_chg >= 100 OR price_chg >= 3 OR price_chg <= -3) ORDER BY vol_chg * avg_daily_volume DESC LIMIT %s"

        self.GET_MARKET_MOVEMENT_MESSAGE_ID = "SELECT message_id FROM ChannelsMessagesIds WHERE message_type = %s AND lang = %s"
        self.UPDATE_MARKET_MOVEMENT_MESSAGE_ID = "UPDATE ChannelsMessagesIds SET message_id = %s, time = NOW() WHERE channel = %s AND message_type = 'mm'"
        self.GET_MESSAGE_ID = "SELECT message_id FROM ChannelsMessagesIds WHERE channel = %s AND message_type = %s"

        self.GET_LEADERS_SPB = "SELECT * FROM DataLeadersSpb ORDER BY id ASC LIMIT %s"
        self.GET_LEADERS_MOEX = "SELECT * FROM DataLeadersMoex ORDER BY id ASC LIMIT %s"
        self.GET_LAST_NEWS_ENG = "SELECT * FROM DataNewsEN WHERE time >= SUBTIME (NOW(), '00:01:10') AND published = 0 ORDER BY id ASC LIMIT %s"
        self.GET_LAST_NEWS_RU = "SELECT * FROM DataNewsRU WHERE time >= SUBTIME (NOW(), '00:01:10') AND published = 0 ORDER BY id ASC LIMIT %s"
        self.UPDATE_NEWS_PUBLISHED_ENG = "UPDATE DataNewsEN SET published = 1 WHERE id = %s"
        self.UPDATE_NEWS_PUBLISHED_RU = "UPDATE DataNewsRU SET published = 1 WHERE id = %s"

        self.GET_NEXT_CALENDAR_NEWS_ENG = "SELECT * FROM DataEconomicCalendarEN WHERE time_published >= ADDTIME (SUBTIME (NOW(), '07:00:00'), '00:09:00') AND time_published <= ADDTIME (SUBTIME (NOW(), '07:00:00'), '00:10:00') ORDER BY id ASC LIMIT %s"
        self.GET_NEXT_CALENDAR_NEWS_RU = "SELECT * FROM DataEconomicCalendarRU WHERE time_published >= ADDTIME (NOW(), '00:09:00') AND time_published <= ADDTIME (NOW(), '00:10:00') ORDER BY id ASC LIMIT %s"
        
        self.GET_DIV_TODAY_RU = "SELECT * FROM DataDividendsMoex WHERE date_expiration = DATE(NOW()) UNION SELECT * FROM DataDividendsSpimex WHERE date_expiration = DATE(NOW()) ORDER BY id ASC LIMIT %s"

        self.__initialize_pool()

    def __initialize_pool(self):
        try:
            self.pool: aiomysql.Connection = db
            logging.info("DB has connected.")
        except Exception as err:
            logging.info(err)
            # logging.exception(err)

    async def __ping(self):
        try:
            command = "SELECT %s"
            args = 1
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(command, args)
                    data = await cur.fetchone()
            # logging.info(data)
            return True
        except Exception as err:
            logging.info(err)
            # logging.exception(err)
            return False

    async def _write_to_db(self, command, args):
        ping = await self.__ping()
        if not ping:
            self.__initialize_pool()

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(command, args)
                await conn.commit()

    async def _get_from_db_fetchone(self, command, args):
        ping = await self.__ping()
        if not ping:
            self.__initialize_pool()

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(command, args)
                return await cur.fetchone()

    async def _get_from_db_fetchall(self, command, args):
        ping = await self.__ping()
        if not ping:
            self.__initialize_pool()

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(command, args)
                return await cur.fetchall()

    async def add_new_user(self):
        user = types.User.get_current()
        chat_id = user.id
        username = user.username if user.username is not None else "-"
        first_name = user.first_name if user.first_name is not None else "-"
        last_name = user.last_name if user.last_name is not None else "-"
        lang = "eng"

        command = self.ADD_NEW_USER
        args = chat_id, username, first_name, last_name, lang
        try:
            await self._write_to_db(command, args)
        except Exception as err:
            logging.info(err)
            # logging.exception(err)
            pass

    async def update_user_lang(self, lang):
        user = types.User.get_current()
        chat_id = user.id

        command = self.UPDATE_USER_LANG
        args = lang, chat_id
        await self._write_to_db(command, args)

    async def insert_newsubscribe(self,
                                  chat_id,
                                  subscribe_channel_id,
                                  subscribe_channel,
                                  subscribe_period,
                                  subscribe_price,
                                  subscribe_status,
                                  payment_status,
                                  payment_amount,
                                  payment_currency,
                                  provider_payment_charge_id,
                                  channel_link,
                                  start_time,
                                  paid_till,
                                  last_notify_time,
                                  reg_time):
        command = self.INSERT_NEWSUBSCRIBE
        args = (chat_id,
                subscribe_channel_id,
                subscribe_channel,
                subscribe_period,
                subscribe_price,
                subscribe_status,
                payment_status,
                payment_amount,
                payment_currency,
                provider_payment_charge_id,
                channel_link,
                start_time,
                paid_till,
                last_notify_time,
                reg_time)
        await self._write_to_db(command, args)

    async def update_newsubscribe(self,
                                  chat_id,
                                  subscribe_status,
                                  payment_status,
                                  provider_payment_charge_id,
                                  channel_link,
                                  start_time,
                                  paid_till,
                                  reg_time):
        command = self.UPDATE_NEWSUBSCRIBE
        args = (subscribe_status,
                payment_status,
                provider_payment_charge_id,
                channel_link,
                start_time,
                paid_till,
                chat_id,
                reg_time)
        await self._write_to_db(command, args)

    async def update_subscribe(self,
                               provider_payment_charge_id,
                               channel_link,
                               paid_till,
                               subscribe_id):
        command = self.UPDATE_SUBSCRIBE
        args = (provider_payment_charge_id,
                channel_link,
                paid_till,
                subscribe_id)
        await self._write_to_db(command, args)

    async def get_user_subscribes(self, chat_id):
        command = self.GET_USER_SUBSCRIBES
        args = chat_id
        data = await self._get_from_db_fetchall(command, args)
        return data

    async def get_user_subscribe(self, chat_id, subscribe_channel_id):
        command = self.GET_USER_SUBSCRIBE
        args = subscribe_channel_id, chat_id
        data = await self._get_from_db_fetchone(command, args)
        return data

    async def get_users_active_subscribes(self):
        command = self.GET_USERS_ACTIVE_SUBSCRIBES
        subscribe_status = "Active"
        args = subscribe_status
        data = await self._get_from_db_fetchall(command, args)
        return data

    async def update_user_subscribe_status(self,
                                           subscribe_channel_id,
                                           chat_id,
                                           subscribe_status,
                                           subscribe_status_previous):
        command = self.UPDATE_USER_SUBSCRIBE_STATUS
        args = (subscribe_status, chat_id, subscribe_channel_id,
                subscribe_status_previous)
        await self._write_to_db(command, args)

    async def update_user_subscribe_last_notify_time(self,
                                                     last_notify_time,
                                                     subscribe_id):
        command = self.UPDATE_USER_SUBSCRIBE_LAST_NOTIFY_TIME
        args = (last_notify_time, subscribe_id)
        await self._write_to_db(command, args)

    async def get_group_all_data(self, group_type):
        command = self.GET_GROUP_ALL_DATA
        args = group_type
        data = await self._get_from_db_fetchall(command, args)
        return data

    async def get_last_market_movements_moex_spb(self, limit):
        command = self.GET_LAST_MARKET_MOVEMENTS_MOEX_SPB
        args = limit
        data = await self._get_from_db_fetchall(command, args)
        return data

    async def get_last_market_movements_spb(self, limit):
        command = self.GET_LAST_MARKET_MOVEMENTS_SPB
        args = limit
        data = await self._get_from_db_fetchall(command, args)
        return data

    async def get_market_movement_message_id(self, lang):
        command = self.GET_MARKET_MOVEMENT_MESSAGE_ID
        args = "mm", lang
        data = await self._get_from_db_fetchall(command, args)
        return data

    async def update_market_movement_message_id(self, message_id, channel):
        command = self.UPDATE_MARKET_MOVEMENT_MESSAGE_ID
        args = message_id, channel
        await self._write_to_db(command, args)

    async def get_message_id(self, channel, message_type):
        command = self.GET_MESSAGE_ID
        args = channel, message_type
        data = await self._get_from_db_fetchone(command, args)
        return data

    async def get_leaders_spb(self):
        command = self.GET_LEADERS_SPB
        args = 20
        data = await self._get_from_db_fetchall(command, args)
        return data

    async def get_leaders_moex(self):
        command = self.GET_LEADERS_MOEX
        args = 20
        data = await self._get_from_db_fetchall(command, args)
        return data

    async def get_last_news_eng(self, limit):
        command = self.GET_LAST_NEWS_ENG
        args = limit
        data = await self._get_from_db_fetchall(command, args)
        return data

    async def get_last_news_ru(self, limit):
        command = self.GET_LAST_NEWS_RU
        args = limit
        data = await self._get_from_db_fetchall(command, args)
        return data

    async def update_news_published(self, news_id, lang):
        command = self.UPDATE_NEWS_PUBLISHED_ENG if lang == "eng" else self.UPDATE_NEWS_PUBLISHED_RU
        args = news_id
        await self._write_to_db(command, args)

    async def get_next_calendar_news_eng(self, limit):
        GET_IMPORTANCE_3 = "SELECT COUNT(importance) AS importance_3 FROM DataEconomicCalendarRU WHERE time_published >= SUBTIME (NOW(), '07:30:00') AND importance = %s"
        GET_CALENDAR_EN_3 = "SELECT * FROM DataEconomicCalendarEN WHERE time_published >= ADDTIME (SUBTIME (NOW(), '07:00:00'), '00:09:00') AND time_published <= ADDTIME (SUBTIME (NOW(), '07:00:00'), '00:10:00') AND importance = 3 ORDER BY time_published ASC, importance DESC LIMIT %s"
        GET_CALENDAR_EN_3_2 = "SELECT * FROM DataEconomicCalendarEN WHERE time_published >= ADDTIME (SUBTIME (NOW(), '07:00:00'), '00:09:00') AND time_published <= ADDTIME (SUBTIME (NOW(), '07:00:00'), '00:10:00') ORDER BY time_published ASC, importance DESC LIMIT %s"
        GET_CALENDAR_EN_2 = "SELECT * FROM DataEconomicCalendarEN WHERE time_published >= ADDTIME (SUBTIME (NOW(), '07:00:00'), '00:09:00') AND time_published <= ADDTIME (SUBTIME (NOW(), '07:00:00'), '00:10:00') AND importance = 2 ORDER BY time_published ASC, importance DESC LIMIT %s"
        command = GET_IMPORTANCE_3
        args = 3
        importance_3 = await self._get_from_db_fetchone(command, args)
        if importance_3["importance_3"] >= 6:
            command = GET_CALENDAR_EN_3
        elif importance_3["importance_3"] >= 1:
            command = GET_CALENDAR_EN_3_2
        else:
            command = GET_CALENDAR_EN_2
        args = 6
        data = await self._get_from_db_fetchall(command, args)
        return data

    async def get_next_calendar_news_ru(self, limit):
        GET_IMPORTANCE_3 = "SELECT COUNT(importance) AS importance_3 FROM DataEconomicCalendarRU WHERE time_published >= SUBTIME (NOW(), '00:30:00') AND importance = %s"
        GET_CALENDAR_RU_3 = "SELECT * FROM DataEconomicCalendarRU WHERE time_published >= ADDTIME (NOW(), '00:09:00') AND time_published <= ADDTIME (NOW(), '00:10:00') AND importance = 3 ORDER BY time_published ASC, importance DESC LIMIT %s"
        GET_CALENDAR_RU_3_2 = "SELECT * FROM DataEconomicCalendarRU WHERE time_published >= ADDTIME (NOW(), '00:09:00') AND time_published <= ADDTIME (NOW(), '00:10:00') ORDER BY time_published ASC, importance DESC LIMIT %s"
        GET_CALENDAR_RU_2 = "SELECT * FROM DataEconomicCalendarRU WHERE time_published >= ADDTIME (NOW(), '00:09:00') AND time_published <= ADDTIME (NOW(), '00:10:00') AND importance = 2 ORDER BY time_published ASC, importance DESC LIMIT %s"
        command = GET_IMPORTANCE_3
        args = 3
        importance_3 = await self._get_from_db_fetchone(command, args)
        if importance_3["importance_3"] >= 6:
            command = GET_CALENDAR_RU_3
        elif importance_3["importance_3"] >= 1:
            command = GET_CALENDAR_RU_3_2
        else:
            command = GET_CALENDAR_RU_2
        args = 6
        data = await self._get_from_db_fetchall(command, args)
        return data

    async def get_div_today_ru(self, limit):
        command = self.GET_DIV_TODAY_RU
        args = limit
        data = await self._get_from_db_fetchall(command, args)
        return data


database = DBCommands()
