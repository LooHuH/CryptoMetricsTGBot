import os
import traceback
import asyncio

from aiogram import Bot, Dispatcher

from modules.config import TG_TOKEN
from modules import commands


async def bot_init():
    dp = Dispatcher()
    bot = Bot(TG_TOKEN)
    await commands.set_up(dp, bot)
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(bot_init())
    except Exception:
        traceback.print_exc()
        os.system('pause')
