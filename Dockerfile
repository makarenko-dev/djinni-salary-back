FROM python:3.13-slim
WORKDIR /usr/src/app

COPY . .

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin/:$PATH"
RUN uv sync
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN chmod +x /usr/src/app/entrypoint.sh
