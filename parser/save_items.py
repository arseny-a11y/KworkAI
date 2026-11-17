from database.database import async_factory
from database.models import KworkProjects
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

async def save_items(data: list[dict]):
    if not data:
        logger.error("[ERROR] | Список проектов пуст...")
        return []

    projects_id = {el.get("project_id") for el in data if el.get("project_id") is not None}

    if not projects_id:
        logger.error("[ERROR] | Не удалось собрать ни одного id проекта")
        return []

    async with async_factory() as session:
        projects_in_db = (await session.scalars(select(KworkProjects).where(KworkProjects.project_id.in_(projects_id)))).all()
        projects_id_in_db = {prj_id.project_id for prj_id in projects_in_db}

        new_projects = []

        for prj in data:
            prj_id = prj.get("project_id")

            if prj_id is not None in projects_id_in_db:
                continue

            new_projects.append(
                KworkProjects(
                    projects_id=prj_id,
                    name=prj.get("name"),
                    description=prj.get("description"),
                    price_limit=prj.get("price_limit"),
                    client_username=prj.get("client_username"),
                    client_hired_percent=prj.get("client_hired_percent"),
                    url=prj.get("url")
                )
            )

        if not new_projects:
            logger.info("[INFO] | Новых проектов не найдено")
            return []
        
        session.add_all(new_projects)
        await session.commit()

        return new_projects