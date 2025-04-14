from typing import AsyncGenerator
from app.uow import UnitOfWork


async def uow() -> AsyncGenerator[UnitOfWork, None]:
    from app.context import app_context

    async with app_context.uow() as uow:
        yield uow
