FROM python:3.13-slim

# Use a specific version of uv to avoid breaking changes
COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app
ADD pyproject.toml /app/
ADD uv.lock /app/
RUN uv sync --frozen --no-dev

ADD alembic.ini /app/
ADD src/ /app/src/

RUN chown -R appuser:appuser /app
USER appuser

ENV PYTHONPATH=/app/src
ENV PATH=/app/.venv/bin:$PATH
ENV APP_ENV=production

EXPOSE 8000

CMD ["fastapi", "run", "src/app/api/main.py", "--app", "app"]