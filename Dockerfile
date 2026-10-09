# syntax=docker/dockerfile:1

ARG PYTHON_IMAGE=python:3.13-slim
FROM ${PYTHON_IMAGE} AS build

WORKDIR /app

# Same pinned official uv release; SHA-256-verified wheels avoid the GHCR
# authorization dependency. Build tooling stays out of the runtime stage.
COPY uv-build-requirements.txt /tmp/uv-build-requirements.txt
RUN python -m pip install \
    --no-cache-dir \
    --no-deps \
    --only-binary=:all: \
    --require-hashes \
    --index-url https://pypi.org/simple \
    --requirement /tmp/uv-build-requirements.txt

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
