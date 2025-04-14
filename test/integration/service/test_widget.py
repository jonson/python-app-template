import pytest
from sqlalchemy.exc import IntegrityError

from app.service.widget import create_widget
from app.uow import UnitOfWork


@pytest.mark.asyncio
async def test_create_widget(uow: UnitOfWork):
    widget = await create_widget(uow, "test")
    assert widget.id is not None
    assert widget.name == "test"


@pytest.mark.asyncio
async def test_create_widget_with_existing_name(testing_uow: UnitOfWork):
    await create_widget(testing_uow, "test")
    with pytest.raises(IntegrityError):
        await create_widget(testing_uow, "test")
