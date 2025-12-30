FROM python:3.13-slim
WORKDIR /usr/src/app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . .

RUN uv sync
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN chmod +x /usr/src/app/entrypoint.sh
