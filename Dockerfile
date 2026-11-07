# Build the application environment with uv.
FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./


# Runtime image without uv.
FROM python:3.12-slim-trixie

RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv
COPY --from=builder --chown=nonroot:nonroot /app/app /app/app
COPY --from=builder --chown=nonroot:nonroot /app/alembic /app/alembic
COPY --from=builder --chown=nonroot:nonroot /app/alembic.ini /app/alembic.ini

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
WORKDIR /app
USER nonroot

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
