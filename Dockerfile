# syntax=docker/dockerfile:1

ARG PYTHON_IMAGE=python:3.13-slim
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.11.29

FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS build

WORKDIR /app

COPY --from=uv /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/foundry

COPY pyproject.toml uv.lock ./

RUN uv sync \
    --frozen \
    --no-dev \
    --no-install-project

COPY alembic.ini ./
COPY alembic alembic
COPY README.md ./
COPY src src

RUN uv sync \
    --frozen \
    --no-dev \
    --no-editable

FROM ${PYTHON_IMAGE} AS runtime

RUN useradd \
    --create-home \
    --uid 10001 \
    --user-group \
    foundry

WORKDIR /app

COPY --from=build /opt/foundry /opt/foundry
COPY --from=build --chown=foundry:foundry /app/alembic.ini ./
COPY --from=build --chown=foundry:foundry /app/alembic ./alembic

ENV PATH="/opt/foundry/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER foundry

ENTRYPOINT ["foundry"]
