import logging

import click

from app.context import setup_default_app_context

logger = logging.getLogger(__name__)


@click.group()
def cli():
    # important, this must be called before any other function to setup the app context
    setup_default_app_context()


@cli.command("hello")
def hello():
    click.echo("Hello, world!")


if __name__ == "__main__":
    cli()
