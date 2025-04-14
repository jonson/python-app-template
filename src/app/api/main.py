from functools import cached_property


def create_app():
    """FastAPI cli doesn't support the app factory pattern, so we play some tricks
    to make it work."""
    from app.context import setup_default_app_context

    setup_default_app_context()
    from starlette.staticfiles import StaticFiles

    from fastapi import FastAPI
    from app.api.routers import main

    app = FastAPI(dependencies=[])
    app.include_router(main.router)
    from pathlib import Path

    # remove this if you don't want to serve static files
    app.mount(
        "/static",
        StaticFiles(directory=Path(__file__).parent.parent.parent / "static"),
        name="static",
    )

    return app


class AppContainer:
    @cached_property
    def app(self):
        return create_app()


app_container = AppContainer()
app = app_container.app
