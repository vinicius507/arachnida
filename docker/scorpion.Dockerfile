FROM python:3.11-slim AS python-base

ARG POETRY_VERSION=1.8.2

ENV DEBIAN_FRONTEND=noninteractive \
	POETRY_HOME=/opt/poetry \
	POETRY_CACHE_DIR=/opt/.cache \
	POETRY_NO_ANSI=1 \
	POETRY_NO_INTERACTION=1 \
	POETRY_VIRTUALENVS_IN_PROJECT=1 \
	POETRY_VIRTUALENVS_CREATE=1 \
	PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	VIRTUAL_ENV=/app/.venv

ENV PATH="${POETRY_HOME}/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
	curl ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache \
	curl -sSL https://install.python-poetry.org | python -

FROM python-base AS python-builder

WORKDIR /app

COPY --from=python-base ${POETRY_HOME} ${POETRY_HOME}
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache \
	poetry install --no-root --only main

FROM python-base AS python-runtime

ENV VIRTUAL_ENV=/app/.venv \
	PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=python-base ${POETRY_HOME} ${POETRY_HOME}
COPY --from=python-builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY pyproject.toml poetry.lock ./
COPY ./scorpion ./scorpion

ENTRYPOINT [ "python", "-m", "scorpion" ]

