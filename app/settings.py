import os

from dotenv import load_dotenv

load_dotenv()
LOG_DIR = os.getenv("LOG_DIR", "log/")
LOG_LEVEL = "INFO"
DEBUG = os.getenv("PROJECT_DEBUG") == "True"
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
SENTRY_DSN = os.getenv("SENTRY_DSN", None)
