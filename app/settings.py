import os

from dotenv import load_dotenv

load_dotenv()
LOG_DIR = os.getenv("LOG_DIR", "log/")
DEBUG = os.getenv("PROJECT_DEBUG") == "True"
LOG_LEVEL = "INFO"
