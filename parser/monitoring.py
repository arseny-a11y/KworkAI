from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder 
from aiogram.types import InlineKeyboardMarkup
from parser.engine import kworkparser
from parser.save_items import save_items
import asyncio
import logging

logger = logging.getLogger(__name__)


def format_text(project: object) -> str:

    name = project.name if project.name else "Название отсутствует"
    description = project.description if project.description else "Описание отсутствует"
    price_limit = project.price_limit if project.price_limit != 0 else "Цена не указана"
    client_username = project.client_username
    client_hired_percent = project.client_hired_percent
    url = project.url if project.url else "Не удалось собрать ссылку"

    message_text = (
      f"🔥 <b>Новый проект на Kwork!</b>\n\n"
      f"📌 <b>{name}</b>\n\n"
      f"💰 <b>Бюджет:</b> {price_limit}\n"
      f"👤 <b>Заказчик:</b> <code>{client_username}</code> (Найм: {client_hired_percent})\n\n"
      f"📝 <b>Описание:</b>\n<i>{description}</i>\n\n"
      f"🔗 <a href='{project.url}'>Открыть проект на Kwork</a>"
    )

    return message_text

def generation_kb(project_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text="✨ Сгенерировать отклик", callback_data=f"prj_generation:{project_id}")
    return kb.as_markup()

async def monitoring_kwork(bot: Bot, chat_id: int, interval: int):
    is_first = True

    try:
        while True:
            try:
                data = await kworkparser.response_api()
                
                project_data = kworkparser.json_parser(data)

                new_projects = await save_items(project_data)

                # if is_first:
                #     if new_projects:
                #         logger.info(f"[INFO] | База успешно инициализирована, сохранено: {len(new_projects)}")
                #     is_first = False

                if new_projects:
                    logger.info(f"[INFO] | Обнаружены новые проекты: {len(new_projects)}")

                    for project in new_projects:
                        text = format_text(project)

                        await bot.send_message(
                            text=text,
                            chat_id=chat_id,
                            parse_mode="HTML",
                            reply_markup=generation_kb(project.project_id)
                        )

                        await asyncio.sleep(0.5)

            except Exception as e:
                logger.exception(f"[ERROR] | Ошибка при работе мониторинга: {e}")

            await asyncio.sleep(interval)

    except asyncio.CancelledError:
        logger.info("[INFO] | Задача мониторинга принудительно остановлена")
        raise

    finally:
        await kworkparser.close()

class MonitorManager:
    def __init__(self):
        self.interval: int = 300
        self._task: asyncio.Task | None = None

    @property
    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def set_interval(self, number: int, bot: Bot, chat_id: int) -> None:
        if self.is_running:
            await self.stop_monitoring()
        
        self.interval = number

        if self.is_running and bot and chat_id:
            await self.start_monitoring(bot, chat_id)

    async def start_monitoring(self, bot: Bot, chat_id: int) -> tuple[bool, str]:
        if self.is_running:
            return False, "⭕ Мониторинг уже активно работает!"
        
        self._task = asyncio.create_task(
            monitoring_kwork(
                bot=bot,
                chat_id=chat_id,
                interval=self.interval
            )
        )
        return True, "✅ Мониторинг успешно запущен!"
    
    async def stop_monitoring(self) -> tuple[bool, str]:
        if not self.is_running:
            return False, "⭕ Мониторинг не был запущен"

        self._task.cancel()
        self._task = None

        return True, "✅ Мониторинг успешно остановлен"

manager = MonitorManager()