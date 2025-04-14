from app.model.widget import Widget
from app.repository.provider import RepositoryProvider
from app.repository.widget import WidgetRepository


async def create_widget(provider: RepositoryProvider, name: str) -> Widget:
    return await provider[WidgetRepository].insert(Widget(name=name))


async def get_widget(provider: RepositoryProvider, widget_id: int) -> Widget | None:
    return await provider[WidgetRepository].get_by_id(widget_id)


def some_math(a: int, b: int) -> int:
    return a + b
