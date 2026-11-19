from config.config import settings
from openai import AsyncOpenAI
from integrations.prompts import KWORK_RESPONSE_PROMPT
import logging
import asyncio

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPEN_ROUTER_API
)

async def response_ai(name: str, description: str):
    name_text = (name or "Название отсутсвует").strip()
    desc_text = (description or "Описание отсутсвует").strip()

    try:
        prompt = KWORK_RESPONSE_PROMPT.format(name=name_text, description=desc_text)

        response = await client.chat.completions.create(
            model="openrouter/free",
            messages=[{"role" : "user", "content" : prompt}]
        )

        answer = (response.choices[0].message.content or "").strip()

        return answer
    
    except Exception as e:
        logger.error(f"[ERROR] | Ошибка при работе с AI: {e}")
        return "❌ Не удалось сгенерировать отклик из-за ошибки ИИ."


async def main():
        name = "Адаптивная верстка по макету Figma на WordPress"
        desc = "Добрый день, уважаемые исполнители.Нужно адаптивно сверстать  1(одну) страницу по макету в Фигме и интегрировать в действующей сайт на WordPress. Подвал можно взять с действующего сайта. Остальные блоки уникальные. Править из админки нужно буквально 2-3 из них, остальные можно сверстать кодом. Макет страницы отрисован как в desktopmobile. Предоставлю ссылку по запросу. Из анимации только изменения цвета логотипов и кнопок при наведении. Работа форм обратной связи на сайте уже настроена, нужно подцепить действующий скрипт к формам, изменив только заголовок письма и добавив поле &quot;Имя&quot;. "
        ai = await response_ai(name, desc)
        print(ai)
if __name__ == "__main__":
    asyncio.run(main())