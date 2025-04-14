import logging
from logging.config import fileConfig

from alembic.script import ScriptDirectory
from sqlalchemy import NullPool

from alembic import context

from app.model.types.datetime import UTCTimestamp

logger = logging.getLogger("alembic.env")


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def process_revision_directives(context, revision, directives):
    # extract Migration
    migration_script = directives[0]

    if getattr(config.cmd_opts, "autogenerate", False):
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
            logger.info("No changes in schema detected.")

    # extract current head revision
    head_revision = ScriptDirectory.from_config(context.config).get_current_head()

    if head_revision is None:
        # edge case with first migration
        new_rev_id = 1
    else:
        # default branch with incrementation
        last_rev_id = int(head_revision.lstrip("0"))
        new_rev_id = last_rev_id + 1
    migration_script.rev_id = f"{new_rev_id:06}"


def render_item(type_, obj, autogen_context):
    """Apply custom rendering for selected items."""

    if type_ == "type" and isinstance(obj, UTCTimestamp):
        return f"sa.{obj.impl!r}"

    # default rendering for other objects
    return False


def run_migrations_offline() -> None:
    raise NotImplementedError("Offline migrations are not supported")


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    from app.context import setup_default_app_context, teardown_app_context

    setup_default_app_context()

    from sqlalchemy import create_engine

    from app.context import app_context

    engine = create_engine(app_context.config.DATABASE_URL, poolclass=NullPool)

    from app.model import METADATA

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=METADATA,
            process_revision_directives=process_revision_directives,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()

    # finally, close the app_context we created
    teardown_app_context()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
