from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, Bot, F
from sqlalchemy import select
from database.database import async_factory
from database.models import KworkProjects
from parser.monitoring import manager
from integrations.openrouter import response_ai
from html import escape

monitor_router = Router()

@monitor_router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "👋 <b>Kwork AI Monitoring Bot</b>\n\n"

        "Бот автоматически отслеживает появление новых проектов в ваших любимых категориях и отправляет в чат.\n\n"

        "📌 <b>Доступные команды:</b>\n"
        "• /set_interval <code>[секунды]</code> — изменить частоту проверки (по умолч. 300 сек)\n"
        "• /start_monitor — запустить фоновый мониторинг\n"
        "• /stop_monitor — остановить мониторинг\n"
        "• /status_monitor — проверить текущее состояние и настройки\n\n"

        "🤖 ПО НАЖАТИЮ КНОПКИ ПОД ПРОЕКТОМ, <b>AI</b> ГЕНЕРИРУЕТ ОТКЛИК ПО ДАННОМУ ПРОЕКТУ"
    )

    await message.answer(text=text, parse_mode="HTML")


@monitor_router.message(Command("start_monitor"))
async def cmd_start_monitor(message: Message, bot: Bot):
    _ , message_text = await manager.start_monitoring(bot, message.chat.id)

    await message.answer(text=message_text)

@monitor_router.message(Command("stop_monitor"))
async def cmd_stop_monitor(message: Message):
    _ , message_text = await manager.stop_monitoring()

    await message.answer(text=message_text)

@monitor_router.message(Command("set_interval"))
async def cmd_set_interval(message: Message, bot: Bot):
    command = message.text.split(maxsplit=1)

    if len(command) != 2:
        return await message.answer(
            "❌ <b>Ошибка в формате команды!</b>\n\n"
            "Отправьте команду вместе с положительным числом (интервал между мониторингом в сек.), например:\n"
            "<code>/set_interval 300</code>", parse_mode="HTML"
        )
    
    text = command[1]

    try:
        number = int(text.strip())
    except ValueError:
        return await message.answer(
            "❌ <b>Ошибка</b>: интервал должен быть целым числом!",
            parse_mode="HTML"
        )

    if number < 60:
        return await message.answer(
            "❌ Минимальное время интервала между мониторингом <b>60 сек.</b>",
            parse_mode="HTML"
        )

    await manager.set_interval(number, bot, message.chat.id)

    await message.answer(
        f"✅ Интервал успешно изменен на <b>{number}</b> сек.",
        parse_mode="HTML"
    )

@monitor_router.message(Command("status_monitor"))
async def cmd_status_monitor(message: Message):
    status = "🟢 Мониторинг проектов успешно работает!" if manager.is_running else "🔴 Мониторинг проектов сейчас не работает"

    text = (
         f"📊 <b>Статус мониторинга:</b> {status}"
    )

    await message.answer(text=text, parse_mode="HTML")

#обработка кнопки нажатия "Сгенерировать отклик"
@monitor_router.callback_query(F.data.startswith("prj_generation:"))
async def generation_response(callback: CallbackQuery):
    await callback.answer("⏳ Генерирую отклик...")
    project_id = int(callback.data.split(":")[-1])

    async with async_factory() as session:

        project = await session.scalar(select(KworkProjects).where(KworkProjects.project_id == project_id))

        if not project:
            return await callback.message.answer("❌ Не удалось найти проект по данному ID")
        
        name = project.name
        description = project.description


    result = await response_ai(name, description)
    # if not result:


    safe_title = escape(name or "Проект без названия")    
    safe_response = escape(result or "Пустой ответ от ИИ")


    if len(safe_response) > 3800:
        safe_response = safe_response[:3800] + "..."

    formatted_text = (
        f"🤖 <b>Отклик готов</b>\n"
        f"📌 <b>Проект:</b> {safe_title}\n\n"
        f"<blockquote>{safe_response}</blockquote>"
    )    

    await callback.message.reply(formatted_text, parse_mode="HTML")