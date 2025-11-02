#!/bin/sh
#nothing here for now
uv run alembic upgrade head

exec "$@"