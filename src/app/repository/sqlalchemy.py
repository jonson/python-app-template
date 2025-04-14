from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyRepository:
    session: AsyncSession

    def __init__(self, session):
        self.session = session
