"""Data layer for the screening scaffold.

Deliberately small. One area table, one task table, and a JSONB column on the
task that holds per-task attributes. This mirrors the shape of the real
SkyTerra schema closely enough that the exercises transfer.
"""

import os

from sqlalchemy import ForeignKey, String, Boolean, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://screen:screen@localhost:55432/screen",
)


class Base(DeclarativeBase):
    pass


class Area(Base):
    __tablename__ = "areas"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(400), nullable=False)
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    # Per-task attributes. `tags` is a list of strings; other keys vary.
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, future=True, expire_on_commit=False)


def init_db():
    Base.metadata.create_all(engine)


def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
