import os

from dotenv import load_dotenv

load_dotenv()
LOG_DIR = os.getenv("LOG_DIR", "log/")
APP_ENV = os.getenv("APP_ENV", "dev").lower()
DEBUG = os.getenv("PROJECT_DEBUG") == "True"
LOG_LEVEL = "INFO"
