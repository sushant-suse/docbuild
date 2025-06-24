# Source: https://docs.astral.sh/uv/guides/integration/docker/#non-editable-installs
#
# Build it with:
# $ docker build -t docbuild:latest .
#  -- or --
# $ docker buildx build -t docbuild:latest .

ARG PYTHON_VERSION=3.13-slim

# ------- Stage 1: Build the environment ----------------
FROM python:${PYTHON_VERSION} AS builder

# Create a non-root user
RUN useradd -m app
USER app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --locked --no-install-project --no-editable

# Copy the project into the intermediate image
ADD --chown=app:app . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --no-editable

# ------- Stage 2: Build/provide the application --------
FROM python:${PYTHON_VERSION}

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Run the application
CMD ["/app/.venv/bin/docbuild"]
