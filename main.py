import logging
from logging.config import dictConfig

dictConfig({
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
            "formatter": "default",
        }
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO"
    },
    "loggers": {
        "backend": {
            "level" : "DEBUG",
            "propagate" : True,
        },
        "frontend": {
            "level" : "DEBUG",
            "propagate" : True,
        },
    }
})

logger = logging.getLogger(__name__)

from frontend.views import visualize_foosball

def main() -> None:
    logger.debug("Main started")
    visualize_foosball()

if __name__ == "__main__":
    main()
