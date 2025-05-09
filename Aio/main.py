import asyncio
import logging
from App.handlers import route
from aiogram import Bot, Dispatcher, F, Router

from Secret import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher() # router обработка обновлений

async def main():
    dp.include_router(route)
    await dp.start_polling(bot) # отправка на сервера тг

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())