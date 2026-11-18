from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, Bot
from parser.monitoring import manager

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