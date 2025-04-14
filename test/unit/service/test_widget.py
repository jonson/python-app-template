import pytest
from app.service.widget import create_widget, some_math
from app.uow import UnitOfWork


def test_some_math():
    assert some_math(1, 2) == 3


@pytest.mark.asyncio
async def test_create_widget(uow: UnitOfWork):
    widget = await create_widget(uow, "test")
    assert widget.name == "test"
    assert widget.id is not None
