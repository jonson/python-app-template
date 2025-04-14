from datetime import datetime
from uuid import UUID

from sqlalchemy import Column
from sqlmodel import Field, SQLModel
from ulid import ULID

from app.model.types.datetime import UTCTimestamp


class Widget(SQLModel, table=True):
    id: UUID = Field(default_factory=lambda: ULID().to_uuid(), primary_key=True)
    name: str = Field(nullable=False, unique=True)

    created_at: datetime = Field(sa_column=Column(UTCTimestamp, server_default="now()"))
