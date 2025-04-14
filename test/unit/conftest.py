import pytest
from app.uow import InMemoryUnitOfWork, UnitOfWork


@pytest.fixture
def uow() -> UnitOfWork:
    return InMemoryUnitOfWork()
