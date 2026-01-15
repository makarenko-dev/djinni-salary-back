import os

from dotenv import load_dotenv

load_dotenv()
LOG_DIR = os.getenv("LOG_DIR", "log/")
LOG_LEVEL = "INFO"
DEBUG = os.getenv("PROJECT_DEBUG") == "True"
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
SENTRY_DSN = os.getenv("SENTRY_DSN", None)
POSTGRES_DB = os.getenv("POSTGRES_DB", None)
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
DB_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

