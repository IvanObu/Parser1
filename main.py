import asyncio
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Db.main_db import parse_and_save, cleanup_old_prices, check_and_notify
from Aio.App.handlers import route
from Secret import TOKEN
import sqlite3
bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(route)

#обновление и уведомление
async def update_and_notify():
    conn = sqlite3.connect("Db/products.db")
    parse_and_save(conn)
    cleanup_old_prices(conn)
    cursor = conn.cursor()
    cursor.execute("SELECT Us_Id FROM User WHERE Us_Id IS NOT NULL")
    result = cursor.fetchone()
    if result:
        user_id = result[0]
        await check_and_notify(conn, bot, user_id)
    else:
        print("❗️ ID пользователя не найден. Уведомление не будет отправлено.")
    conn.close()
    print("✅ Данные обновлены и уведомления отправлены.")

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_and_notify, "interval", minutes=5)
    scheduler.start()

    await update_and_notify()

    # 🔹 Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
