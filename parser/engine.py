from curl_cffi.requests import AsyncSession
from curl_cffi.requests.exceptions import HTTPError, RequestException
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

class KworkParser:

    def __init__(self, cookies: dict, url: str = "https://kwork.ru/projects"):
        self.url = url
        self.cookies = self._load_cookies()
        self.session = None
        self.headers = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 YaBrowser/26.10.0.0 Safari/537.36",
            "Accept-Language" : "ru,en;q=0.9,ko;q=0.8",
            "Accept" : "application/json, text/plain, */*",
            "X-Requested-With" : "XMLHttpRequest",
            "Referer": "https://kwork.ru/projects"
        }

    
    def _load_cookies(self):
        try:
            #измените путь, если куки лежат в другом месте
            with open("parser/cookies.json","r", encoding="utf-8") as file:
                data = json.load(file)
                
            if isinstance(data, list):
                return {cookie["name"]: cookie["value"] for cookie in data}
            return data
        except FileNotFoundError:
            logger.error("[ERROR] | Файл с куками не найден!")
            return {}
        except Exception as e:
            logger.error(f"[ERROR] | Ошибка при чтение куков: {e}")

    #открываем сессию, если она еще не создана
    async def _start(self):
        if not self.session:
            self.session = AsyncSession()

    #закрываем сессию, если она существует
    async def _close(self):
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("[INFO] | Сессия парсера закрыта")

    async def response_api(self) -> dict:
        await self._start()
        try:
            response = await self.session.post(
                url=self.url,
                cookies=self.cookies,
                headers=self.headers,
                impersonate='chrome120',
                timeout=15.0
            )
            
            response.raise_for_status()
            data = response.json()

            logger.info("[SUCCESS] | Данные успешно получены !")
            return data

        except HTTPError as e:
            logger.error(f"[ERROR] | Cтатус запроса: {e.response.status_code}")
            return {}
        
        except RequestException as e:
            logger.error(f"[ERROR] | Сервер разорвал соединение: {e}")
            return {}
        
        except Exception as e:
            logger.error(f"[ERROR] | Непредвиденная ошибка: {e}")
            return {}


    def json_parser(self, data: dict) -> list[dict]:
        if not data:
            logger.info("[INFO] | Словарь не содержит данных")
            return []
        
        response_data = data.get("data", {})
        orders = response_data.get("wants") if response_data else None

        if not orders:
            logger.error(
                "[ERROR] | В полученном ответе отсутствуют заказы (ключ wants не"
                " найден)."
            )
            return []

        project_info = []
        set_ids = set()

        for order in orders:

            #проверяем заказ на дубликаты
            project_id = order.get("id")
            if not project_id or project_id in set_ids:
                continue
            set_ids.add(project_id)

            #безопасно достаем данные
            name = (order.get("name") or "").replace("\r", "").replace("\n", "")
            description = (order.get("description") or "").replace("\r", "").replace("\n", "")

            user = order.get("user", {})
            
            project_info.append({
                "id" : project_id,
                "name" : name,
                "description" : description,
                "price_limit" : order.get("priceLimit"),
                "client_username" : user.get("username", "Отсутствует"),
                "client_hired_percent" : user.get("data", {}).get("wants_hired_percent"),
                "url" : f"{self.url}/{project_id}/view"
            })

        return project_info
    
async def main():

    

    parser = KworkParser()

    data = await parser.response_api()
    print(len(parser.json_parser(data)))

if __name__ == "__main__":
    asyncio.run(main())