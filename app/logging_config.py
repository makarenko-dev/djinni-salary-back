import os
from logging.config import dictConfig

LOG_DIR = os.getenv("LOG_DIR", "log/")
APP_ENV = os.getenv("APP_ENV", "dev").lower()
LOG_LEVEL = "INFO"


def build_logging_config() -> dict:
    common_format = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    dev_format = "%(levelname)s: %(message)s"

    # Handlers
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "dev" if APP_ENV == "dev" else "prod",
            "stream": "ext://sys.stdout",
        }
    }

    if APP_ENV == "prod":
        os.makedirs(LOG_DIR, exist_ok=True)
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": LOG_LEVEL,
            "formatter": "prod",
            "filename": os.path.join(LOG_DIR, "app.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        }

    # Formatters
    formatters = {
        "dev": {
            "format": dev_format,
        },
        "prod": {
            "format": common_format,
        },
    }
    loggers = {
        "": {
            "handlers": list(handlers.keys()),
            "level": LOG_LEVEL,
        },
        "sqlalchemy.engine": {"level": "WARNING"},
    }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": handlers,
        "loggers": loggers,
    }


def configure_logging() -> None:
    dictConfig(build_logging_config())
