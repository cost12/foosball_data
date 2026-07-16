import logging
from logging.config import dictConfig
from pathlib import Path
import json

import pydantic

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
from backend import data_models

def main() -> None:
    visualize_foosball()

DATA = Path(r"C:\Users\miles\OneDrive\Documents\coding\foosball_data\data")

def test():
    with (DATA / "models/input.json").open('r', encoding='utf-8') as f:
        data_spec_raw = json.load(f)

    data_spec = data_models.DataSpecification.model_validate(data_spec_raw)
    logger.debug(data_spec)

if __name__ == "__main__":
    #main()
    test()
