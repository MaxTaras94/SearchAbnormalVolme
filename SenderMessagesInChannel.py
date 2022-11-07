# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 15:35:52 2021

@author: taras
"""


from aiogram import Bot
from aiogram.types import ParseMode
from data.config import TOKEN, channel_id

class SenderMessagesInChannel():
    def __init__(self):
        self.BOT = TOKEN
        self.bot = Bot(self.BOT, parse_mode=ParseMode.HTML)
    
    async def send_message(self, message):
        await self.bot.send_message(
            chat_id=channel_id,
            text=message,
            disable_web_page_preview=True)

sender = SenderMessagesInChannel()

if __name__ == "__main__":
    sender = SenderMessagesInChannel()
    sender.send_message('Test')