from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession 
import asyncio
import logging
from config.config import settings

async def main():
    
    logging.basicConfig(level=logging.INFO)
    session = AiohttpSession(proxy=settings.PROXY)

    bot = Bot(settings.TOKEN, session=session)
    dp = Dispatcher()

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