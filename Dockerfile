FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
ADD . /app

# Install dependencies
RUN uv sync --frozen --no-install-project

# Sync the project
RUN uv sync --frozen

CMD ["uv", "run", "main.py"]
