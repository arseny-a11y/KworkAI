from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import Integer, String, Text, DateTime, func
from datetime import datetime

class Base(DeclarativeBase):
    pass

class KworkProjects(Base):
    __tablename__ = "kwork_projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price_limit: Mapped[int] = mapped_column(Integer, nullable=True)
    client_username: Mapped[str] = mapped_column(String(64), nullable=True)
    client_hired_percent: Mapped[int] = mapped_column(Integer, nullable=True)
    url: Mapped[str] = mapped_column(String(255))
