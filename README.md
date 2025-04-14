# FastAPI Project Template

This repo is a quick-start for a deployable FastAPI application.

## Dependencies

`uv` is used for dependency management.

```
uv sync
```

```
# normal applicaiton deps
uv add fastapi

# dev deps
uv add --dev import-linter
```

## Tasks

`mise` is setup to run some tasks, `mise tasks` for more info.

## Cli commands

```bash
python -m app.cmd hello
```


## FastAPI
Development:

```bash
uv run fastapi dev src/app/api/main.py --app app
```

## Migrations

### Creating
```
uv run alembic revision --autogenerate -m "Initial version"
```

### Updating
```
uv run alembic upgrade head
```

## Production build

A Dockerfile is provided for convience.