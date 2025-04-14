import os
from pathlib import Path
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from sqlalchemy import Connection, create_engine, text
from app.utils.env import ensure_psycopg_url
from app.context import TESTING_APP_ENV, setup_default_app_context, app_context
from app.uow import UnitOfWork
from testcontainers.postgres import PostgresContainer


from alembic.config import Config
from alembic import command


def run_migrations(script_location: str, dsn: str) -> None:
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_cfg.set_main_option("sqlalchemy.url", dsn)
    command.upgrade(alembic_cfg, "head")


SNAPSHOT_DB_NAME = "snapshot"


@pytest.fixture(autouse=True, scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:

    with PostgresContainer("postgres:17.2") as container:
        db_url = container.get_connection_url(driver=None)
        os.environ["DATABASE_URL"] = db_url

        migrations_dir = Path(__file__).parent.parent.parent / "src" / "migrations"
        run_migrations(
            script_location=str(migrations_dir),
            dsn=db_url,
        )

        yield container


@pytest.fixture(autouse=True, scope="session")
def admin_db_connection(
    postgres_container: PostgresContainer,
) -> Generator[Connection, None, None]:
    db_url = postgres_container.get_connection_url(driver=None)
    # we need to connect to the template1 database for this admin connection, otherwise the create and
    # drop commands will fail because we're connected to it.  template1 is a special database in postgres.
    db_url = db_url[: -len(postgres_container.dbname)] + "template1"
    engine = create_engine(ensure_psycopg_url(db_url))
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        yield conn


@pytest.fixture(autouse=True, scope="session")
def _create_snapshot(
    admin_db_connection: Connection, postgres_container: PostgresContainer
):
    admin_db_connection.execute(
        text(
            f"create database {SNAPSHOT_DB_NAME} template {postgres_container.dbname};"
        )
    )


@pytest.fixture(autouse=True)
def _app_context():
    setup_default_app_context(app_env=TESTING_APP_ENV)


@pytest_asyncio.fixture(autouse=True)
async def _restore_db_snapshot(
    admin_db_connection: Connection, postgres_container: PostgresContainer
):
    yield

    # # we need to dispose of the async engine before restoring the snapshot
    await app_context.async_engine.dispose()

    # restore the snapshot after each test
    admin_db_connection.execute(
        text(
            f"select pg_terminate_backend(pid) from pg_stat_activity where datname='{postgres_container.dbname}';"
        )
    )
    admin_db_connection.execute(text(f"drop database {postgres_container.dbname}"))
    admin_db_connection.execute(
        text(
            f"create database {postgres_container.dbname} template {SNAPSHOT_DB_NAME};"
        )
    )


@pytest_asyncio.fixture
async def uow() -> AsyncGenerator[UnitOfWork, None]:
    async with app_context.uow() as uow:
        yield uow


@pytest_asyncio.fixture
async def testing_uow() -> AsyncGenerator[UnitOfWork, None]:
    """Variant of a uow that will not get angry if there's a pending rollback.  This
    is normally not needed, the regular uow will suffice.  Once a bad operation occurs on a
    sqlalchemy session, it must be rolled back."""
    from app.uow import TestingSqlAlchemyUnitOfWork

    async with TestingSqlAlchemyUnitOfWork() as uow:
        yield uow
