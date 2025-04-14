from functools import cached_property
import os

from dotenv import load_dotenv
from app.utils.proxy import StackTopProxy

from app.config import Config


class DefaultAppContext:
    @cached_property
    def config(self):
        return Config()

    @cached_property
    def uow(self):
        from app.uow import SqlAlchemyUnitOfWork

        return SqlAlchemyUnitOfWork

    @cached_property
    def async_engine(self):
        from sqlalchemy.ext.asyncio import create_async_engine

        return create_async_engine(
            self.config.DATABASE_URL,
        )

    @cached_property
    def sync_engine(self):
        from sqlalchemy import create_engine

        return create_engine(
            self.config.DATABASE_URL,
        )


class DevelopmentAppContext(DefaultAppContext):
    @cached_property
    def config(self):
        from app.config import DevelopmentConfig

        return DevelopmentConfig()


class TestingAppContext(DefaultAppContext):
    @cached_property
    def config(self):
        from app.config import TestConfig

        return TestConfig()

    # @cached_property
    # def uow(self):
    #     from app.uow import TestingSqlAlchemyUnitOfWork

    #     return TestingSqlAlchemyUnitOfWork


app_context_stack = StackTopProxy[DefaultAppContext]()
app_context = app_context_stack.top_proxy


# for pytest
TESTING_APP_ENV = "testing"

# local development
LOCAL_DEV_APP_ENV = "local"

# production (anything outside of local development)
PRODUCTION_APP_ENV = "production"


def setup_default_app_context(app_env: str | None = None):
    if app_context_stack.top:
        return

    # load .env
    load_dotenv()

    if app_env is None:
        app_env = os.getenv("APP_ENV", LOCAL_DEV_APP_ENV)

    if app_env == PRODUCTION_APP_ENV:
        ctx = DefaultAppContext()
    elif app_env == LOCAL_DEV_APP_ENV:
        ctx = DevelopmentAppContext()
    elif app_env == TESTING_APP_ENV:
        ctx = TestingAppContext()
    else:
        raise ValueError(f"Invalid app environment: {app_env}")

    app_context_stack.push(ctx)


def teardown_app_context():
    app_context_stack.pop()
