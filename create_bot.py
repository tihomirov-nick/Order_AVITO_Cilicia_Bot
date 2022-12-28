from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

storage = MemoryStorage()

bot = Bot(token=('5718271765:AAGE8QHpMr6tjn7t2sOIrHej3UkTgWFbb3Q'))
dp = Dispatcher(bot, storage=storage)
