from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession 
from config.config import settings
from database.database import init_db
from handlers.commands import monitor_router
import asyncio
import logging
async def main():

    logging.basicConfig(level=logging.INFO)
    session = AiohttpSession(proxy=settings.PROXY)

    
    bot = Bot(settings.TOKEN, session=session)
    dp = Dispatcher()

    await init_db()
    dp.include_router(monitor_router)
    try:
        print("Бот запущен!")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    finally:
        await bot.session.close()
        
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен!")