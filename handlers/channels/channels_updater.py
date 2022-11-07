from aiogram import Bot
from aiogram.types import InputMedia, ParseMode
import asyncio
from data.config import (DATA_DIR,
                         PAY_BOT_TRADERHELPER_TOKEN,
                         TRADERHELPER_ID,
                         QUOTE_TRADERHELPER_ID,
                         MM_TRADERHELPER_ID,
                         NEWS_TRADERHELPER_ID,
                         RU_TRADERHELPER_ID,
                         RU_QUOTE_TRADERHELPER_ID,
                         RU_MM_TRADERHELPER_ID,
                         RU_NEWS_TRADERHELPER_ID,
                         THCU_FOREX_1_BOT_TOKEN,
                         THCU_FOREX_2_BOT_TOKEN,
                         THCU_FOREX_3_BOT_TOKEN,
                         THCU_FOREX_4_BOT_TOKEN,
                         THCU_COMMODITIES_1_BOT_TOKEN,
                         THCU_COMMODITIES_2_BOT_TOKEN,
                         THCU_COMMODITIES_3_BOT_TOKEN,
                         THCU_COMMODITIES_4_BOT_TOKEN,
                         THCU_INDEXES_1_BOT_TOKEN,
                         THCU_INDEXES_2_BOT_TOKEN,
                         THCU_INDEXES_3_BOT_TOKEN,
                         THCU_INDEXES_4_BOT_TOKEN,
                         THCU_CRYPTO_1_BOT_TOKEN,
                         THCU_CRYPTO_2_BOT_TOKEN,
                         THCU_CRYPTO_3_BOT_TOKEN,
                         THCU_CRYPTO_4_BOT_TOKEN,
                         THCU_DASHBOARD_1_BOT_TOKEN,
                         THCU_DASHBOARD_2_BOT_TOKEN,
                         THCU_DASHBOARD_3_BOT_TOKEN,
                         THCU_DASHBOARD_4_BOT_TOKEN,
                         THCU_LEADERS_1_BOT_TOKEN,
                         THCU_LEADERS_2_BOT_TOKEN,
                         THCU_MM_1_BOT_TOKEN,
                         THCU_MM_2_BOT_TOKEN,
                         THCU_NEWS_RU_1_BOT_TOKEN)
import os
import datetime
from data.market_movement_text import market_movement_text_eng_rus
from data.quotes_message_text import quotes_message_text
import logging
from utils.db_api.db_commands import database
from utils.mt5.mt5_integration import mt5quotes


class Channels():
    """
    Обновление каналов.
    Groups это сообщения в каналах, которые обновляем.
    Каждое сообщение объеденяет тикеры к свою группу.
    Получение data происходит или из бд или из mt5.
    """

    def __init__(self):
        self.PAY_BOT_TRADERHELPER = Bot(token=PAY_BOT_TRADERHELPER_TOKEN,
                                        parse_mode=ParseMode.HTML)

        self.TRADERHELPER_NAME = "ToTraders"
        self.TRADERHELPER_ID = TRADERHELPER_ID
        self.QUOTE_TRADERHELPER_NAME = "QuoteToTraders"
        self.QUOTE_TRADERHELPER_ID = QUOTE_TRADERHELPER_ID
        self.MM_TRADERHELPER_ID = MM_TRADERHELPER_ID
        self.NEWS_TRADERHELPER_ID = NEWS_TRADERHELPER_ID

        self.RU_TRADERHELPER_NAME = "RuToTraders"
        self.RU_TRADERHELPER_ID = RU_TRADERHELPER_ID
        self.RU_QUOTE_TRADERHELPER_NAME = "QuoteRuToTraders"
        self.RU_QUOTE_TRADERHELPER_ID = RU_QUOTE_TRADERHELPER_ID
        self.RU_MM_TRADERHELPER_ID = RU_MM_TRADERHELPER_ID
        self.RU_NEWS_TRADERHELPER_ID = RU_NEWS_TRADERHELPER_ID

        self.THCU_FOREX_1_BOT = Bot(token=THCU_FOREX_1_BOT_TOKEN,
                                    parse_mode=ParseMode.HTML)
        self.THCU_FOREX_2_BOT = Bot(token=THCU_FOREX_2_BOT_TOKEN,
                                    parse_mode=ParseMode.HTML)
        self.THCU_FOREX_3_BOT = Bot(token=THCU_FOREX_3_BOT_TOKEN,
                                    parse_mode=ParseMode.HTML)
        self.THCU_FOREX_4_BOT = Bot(token=THCU_FOREX_4_BOT_TOKEN,
                                    parse_mode=ParseMode.HTML)
        self.THCU_COMMODITIES_1_BOT = Bot(
            token=THCU_COMMODITIES_1_BOT_TOKEN,
            parse_mode=ParseMode.HTML)
        self.THCU_COMMODITIES_2_BOT = Bot(
            token=THCU_COMMODITIES_2_BOT_TOKEN,
            parse_mode=ParseMode.HTML)
        self.THCU_COMMODITIES_3_BOT = Bot(
            token=THCU_COMMODITIES_3_BOT_TOKEN,
            parse_mode=ParseMode.HTML)
        self.THCU_COMMODITIES_4_BOT = Bot(
            token=THCU_COMMODITIES_4_BOT_TOKEN,
            parse_mode=ParseMode.HTML)
        self.THCU_INDEXES_1_BOT = Bot(token=THCU_INDEXES_1_BOT_TOKEN,
                                      parse_mode=ParseMode.HTML)
        self.THCU_INDEXES_2_BOT = Bot(token=THCU_INDEXES_2_BOT_TOKEN,
                                      parse_mode=ParseMode.HTML)
        self.THCU_INDEXES_3_BOT = Bot(token=THCU_INDEXES_3_BOT_TOKEN,
                                      parse_mode=ParseMode.HTML)
        self.THCU_INDEXES_4_BOT = Bot(token=THCU_INDEXES_4_BOT_TOKEN,
                                      parse_mode=ParseMode.HTML)
        self.THCU_CRYPTO_1_BOT = Bot(token=THCU_CRYPTO_1_BOT_TOKEN,
                                     parse_mode=ParseMode.HTML)
        self.THCU_CRYPTO_2_BOT = Bot(token=THCU_CRYPTO_2_BOT_TOKEN,
                                     parse_mode=ParseMode.HTML)
        self.THCU_CRYPTO_3_BOT = Bot(token=THCU_CRYPTO_3_BOT_TOKEN,
                                     parse_mode=ParseMode.HTML)
        self.THCU_CRYPTO_4_BOT = Bot(token=THCU_CRYPTO_4_BOT_TOKEN,
                                     parse_mode=ParseMode.HTML)
        self.THCU_DASHBOARD_1_BOT = Bot(token=THCU_DASHBOARD_1_BOT_TOKEN,
                                        parse_mode=ParseMode.HTML)
        self.THCU_DASHBOARD_2_BOT = Bot(token=THCU_DASHBOARD_2_BOT_TOKEN,
                                        parse_mode=ParseMode.HTML)
        self.THCU_DASHBOARD_3_BOT = Bot(token=THCU_DASHBOARD_3_BOT_TOKEN,
                                        parse_mode=ParseMode.HTML)
        self.THCU_DASHBOARD_4_BOT = Bot(token=THCU_DASHBOARD_4_BOT_TOKEN,
                                        parse_mode=ParseMode.HTML)
        self.THCU_LEADERS_1_BOT = Bot(token=THCU_LEADERS_1_BOT_TOKEN,
                                      parse_mode=ParseMode.HTML)
        self.THCU_LEADERS_2_BOT = Bot(token=THCU_LEADERS_2_BOT_TOKEN,
                                      parse_mode=ParseMode.HTML)
        self.THCU_MM_1_BOT = Bot(token=THCU_MM_1_BOT_TOKEN,
                                 parse_mode=ParseMode.HTML)
        self.THCU_MM_2_BOT = Bot(token=THCU_MM_2_BOT_TOKEN,
                                 parse_mode=ParseMode.HTML)
        self.THCU_NEWS_RU_1_BOT = Bot(token=THCU_NEWS_RU_1_BOT_TOKEN,
                                      parse_mode=ParseMode.HTML)

    async def update_quotes_group(self, bot, group_type, channels, cache_time):
        """0 - quote channel, 1 - main channel
        mtime - last change time"""
        data = mt5quotes.run(group_type)
        for i in range(2):
            lang = "eng" if i < 1 else "rus"
            text, mtime = quotes_message_text(data[0], group_type, lang)
            if mtime != cache_time:
                try:
                    await bot.edit_message_text(
                        chat_id=channels[i]["channel_id"],
                        message_id=channels[i]["group_message_id"],
                        text=text)
                except Exception as err:
                    logging.info(err)
        return mtime


    async def update_mm_group(self, bot, channels, lang):
        """
        Получаем market_movement_message_id из bd
        0 - full channel, 1 - main channel
        """
        mm_message_ids = await database.get_market_movement_message_id(lang)

        if lang == "eng":
            data = await database.get_last_market_movements_spb(limit=1)
        else:
            data = await database.get_last_market_movements_moex_spb(limit=1)
        if len(data) > 0:
            text = market_movement_text_eng_rus(
                instruction_link=channels[0]["instruction_link"],
                first_quotes_link=channels[0]["first_quotes_link"],
                row=data[0],
                lang=lang)
            try:
                await bot.delete_message(
                    chat_id=channels[0]["channel_id"],
                    message_id=mm_message_ids[0]["message_id"])
            except Exception as err:
                logging.info(err)
            try:
                message = await bot.send_message(
                    chat_id=channels[0]["channel_id"],
                    text=text,
                    disable_web_page_preview=True)
                await database.update_market_movement_message_id(
                    message["message_id"], channels[0]["channel"])
            except Exception as err:
                logging.info(err)
        else:
            text = market_movement_text_eng_rus(
                instruction_link=channels[0]["instruction_link"],
                first_quotes_link=channels[0]["first_quotes_link"],
                lang=lang)
            try:
                await bot.edit_message_text(
                    chat_id=channels[0]["channel_id"],
                    message_id=mm_message_ids[0]["message_id"],
                    text=text,
                    disable_web_page_preview=True)
            except Exception as err:
                logging.info(err)

    async def send_mm_to_mm_channel(self, bot, channel_id, lang, limit):
        if lang == "eng":
            mms = await database.get_last_market_movements_spb(
                limit=limit)
        else:
            mms = await database.get_last_market_movements_moex_spb(
                limit=limit)
        if len(mms) > 0:
            for mm in mms:
                text = market_movement_text_eng_rus(row=mm, links=False,
                                                    lang=lang)
                try:
                    await bot.send_message(
                        chat_id=channel_id,
                        text=text,
                        disable_web_page_preview=True)
                except Exception as err:
                    logging.info(err)



class ChannelsUpdater():
    """
    Запуск постоянного обновления канала.
    Инициализируем канал который будем обновлять.
    Запускаем его методы update_() через параллельные таски.
    FPS [сек] частота обновления группы сообщений канала.

    Ограничения
    MAX_MESSAGES_PER_MINUTE_PER_GROUP = 20
    """

    def __init__(self):
        self._FPS_QUOTES_FOREX = 1
        self._FPS_QUOTES_COMMODITIES = 1
        self._FPS_QUOTES_INDEXES = 1
        self._FPS_QUOTES_CRYPTO = 1

        # Инициализируем каналы и запускаем обновления
        self._channels = Channels()
        self.forex = asyncio.create_task(
            self._update_quotes_forex())
        self.commodities = asyncio.create_task(
            self._update_quotes_commodities())
        self.indexes = asyncio.create_task(
            self._update_quotes_indexes())
        self.crypto = asyncio.create_task(
            self._update_quotes_crypto())
        self.dashboard_eng = asyncio.create_task(
            self._update_dashboard_eng_pic())
        self.dashboard_rus = asyncio.create_task(
            self._update_dashboard_rus_pic())
        self.leaders_eng = asyncio.create_task(
            self._send_leaders_eng_pic())
        self.leaders_rus = asyncio.create_task(
            self._send_leaders_rus_pic())
        self.mm = asyncio.create_task(
            self._update_mm())
        self.ru_mm = asyncio.create_task(
            self._update_ru_mm())
        self.news = asyncio.create_task(
            self._update_news())
        self.ru_news = asyncio.create_task(
            self._update_ru_news())
        self.ru_dividends = asyncio.create_task(
            self._update_ru_dividends())

    async def _update_quotes_forex(self):
        finished = False
        group_type = "forex"
        bots = [self._channels.THCU_FOREX_1_BOT,
                self._channels.THCU_FOREX_2_BOT,
                self._channels.THCU_FOREX_3_BOT,
                self._channels.THCU_FOREX_4_BOT]
        channels = [{"channel_id": self._channels.TRADERHELPER_ID,
                     "group_message_id": 6},
                    {"channel_id": self._channels.RU_TRADERHELPER_ID,
                     "group_message_id": 4}]
        i = 0
        cache_time = 0
        while not finished:
            try:
                cache_time = await self._channels.update_quotes_group(
                    bot=bots[i],
                    group_type=group_type,
                    channels=channels,
                    cache_time=cache_time)
            except Exception as err:
                logging.info(err)
            i = i + 1 if i < 3 else 0
            await asyncio.sleep(self._FPS_QUOTES_FOREX)

    async def _update_quotes_commodities(self):
        finished = False
        group_type = "commodities"
        bots = [self._channels.THCU_COMMODITIES_1_BOT,
                self._channels.THCU_COMMODITIES_2_BOT,
                self._channels.THCU_COMMODITIES_3_BOT,
                self._channels.THCU_COMMODITIES_4_BOT]
        channels = [{"channel_id": self._channels.TRADERHELPER_ID,
                     "group_message_id": 7},
                    {"channel_id": self._channels.RU_TRADERHELPER_ID,
                     "group_message_id": 5}]
        i = 0
        cache_time = 0
        while not finished:
            try:
                cache_time = await self._channels.update_quotes_group(
                    bot=bots[i],
                    group_type=group_type,
                    channels=channels,
                    cache_time=cache_time)
            except Exception as err:
                logging.info(err)
            i = i + 1 if i < 3 else 0
            await asyncio.sleep(self._FPS_QUOTES_COMMODITIES)

    async def _update_quotes_indexes(self):
        finished = False
        group_type = "indexes"
        bots = [self._channels.THCU_INDEXES_1_BOT,
                self._channels.THCU_INDEXES_2_BOT,
                self._channels.THCU_INDEXES_3_BOT,
                self._channels.THCU_INDEXES_4_BOT]
        channels = [{"channel_id": self._channels.TRADERHELPER_ID,
                     "group_message_id": 8},
                    {"channel_id": self._channels.RU_TRADERHELPER_ID,
                     "group_message_id": 6}]
        i = 0
        cache_time = 0
        while not finished:
            try:
                cache_time = await self._channels.update_quotes_group(
                    bot=bots[i],
                    group_type=group_type,
                    channels=channels,
                    cache_time=cache_time)
            except Exception as err:
                logging.info(err)
            i = i + 1 if i < 3 else 0
            await asyncio.sleep(self._FPS_QUOTES_INDEXES)

    async def _update_quotes_crypto(self):
        finished = False
        group_type = "crypto"
        bots = [self._channels.THCU_CRYPTO_1_BOT,
                self._channels.THCU_CRYPTO_2_BOT,
                self._channels.THCU_CRYPTO_3_BOT,
                self._channels.THCU_CRYPTO_4_BOT]
        channels = [{"channel_id": self._channels.TRADERHELPER_ID,
                     "group_message_id": 9},
                    {"channel_id": self._channels.RU_TRADERHELPER_ID,
                     "group_message_id": 7}]
        i = 0
        cache_time = 0
        while not finished:
            try:
                cache_time = await self._channels.update_quotes_group(
                    bot=bots[i],
                    group_type=group_type,
                    channels=channels,
                    cache_time=cache_time)
            except Exception as err:
                logging.info(err)
            i = i + 1 if i < 3 else 0
            await asyncio.sleep(self._FPS_QUOTES_CRYPTO)


    async def _update_ru_mm(self):
        finished = False
        channels = [{"channel_id": self._channels.RU_TRADERHELPER_ID,
                     "channel": self._channels.RU_TRADERHELPER_NAME,
                     "instruction_link": "https://t.me/RuToTraders/3",
                     "first_quotes_link": "https://t.me/RuToTraders/4"}]
        while not finished:
            time = datetime.datetime.today()
            delta = (60 - time.second) + 40
            await asyncio.sleep(delta)
            try:
                await self._channels.update_mm_group(
                    bot=self._channels.THCU_MM_1_BOT,
                    channels=channels,
                    lang="rus")
            except Exception as err:
                logging.info(err)
            try:
                await self._channels.send_mm_to_mm_channel(
                    bot=self._channels.THCU_MM_1_BOT,
                    channel_id=self._channels.RU_MM_TRADERHELPER_ID,
                    lang="rus",
                    limit=20)
            except Exception as err:
                logging.info(err)

