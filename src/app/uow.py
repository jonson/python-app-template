import abc
from functools import cache
from typing import TypeVar, cast

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import PendingRollbackError
from app.context import app_context
from app.repository.provider import RepositoryProvider
from app.repository.registry import IN_MEMORY_REGISTRY, REGISTRY

TRepository = TypeVar("TRepository")


class UnitOfWork(RepositoryProvider, abc.ABC):
    async def __aenter__(self, *args):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    @abc.abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        raise NotImplementedError

    async def flush(self):
        pass


@cache
def session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker[AsyncSession](bind=app_context.async_engine)


def default_session_factory():
    return session_maker()()


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory=default_session_factory):
        self.session_factory = session_factory
        self._registry = REGISTRY

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    def __getitem__(self, base_repository_class: type[TRepository]) -> TRepository:
        repository_class = self._registry[base_repository_class]
        repository = repository_class(self.session)
        return cast(TRepository, repository)

    async def flush(self):
        await self.session.flush()


class TestingSqlAlchemyUnitOfWork(SqlAlchemyUnitOfWork):

    async def commit(self):
        try:
            await self.session.commit()
        except PendingRollbackError:
            await self.session.rollback()


class InMemoryUnitOfWork(UnitOfWork):
    def __init__(self):
        self._registry = IN_MEMORY_REGISTRY
        self.committed = False
        self.rolled_back = False

    def __getitem__(self, base_repository_class: type[TRepository]) -> TRepository:
        repository_class = self._registry[base_repository_class]
        repository = repository_class()
        return repository

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True
