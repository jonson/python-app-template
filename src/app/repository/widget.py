from uuid import UUID

from ulid import ULID
from app.model.widget import Widget
from app.repository.registry import IN_MEMORY_REGISTRY, register
from app.repository.sqlalchemy import SqlAlchemyRepository


class WidgetRepository:

    async def get_by_id(self, widget_id: UUID | ULID | str) -> Widget | None:
        raise NotImplementedError

    async def insert(self, widget: Widget) -> Widget:
        raise NotImplementedError


@register(WidgetRepository)
class SqlAlchemyWidgetRepository(WidgetRepository, SqlAlchemyRepository):

    async def get_by_id(self, widget_id: UUID | ULID | str) -> Widget | None:
        if isinstance(widget_id, ULID):
            widget_id = widget_id.to_uuid()
        return await self.session.get(Widget, widget_id)

    async def insert(self, widget: Widget) -> Widget:
        self.session.add(widget)
        await self.session.flush()
        return widget


@register(WidgetRepository, registry=IN_MEMORY_REGISTRY)
class InMemoryWidgetRepository(WidgetRepository):
    def __init__(self):
        self.widgets = {}

    async def insert(self, widget: Widget) -> Widget:
        self.widgets[widget.id] = widget
        return widget

    async def get_by_id(self, widget_id: UUID | ULID | str) -> Widget | None:
        return self.widgets.get(widget_id)
