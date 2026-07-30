import logging
from logging.config import dictConfig
from pathlib import Path
import json

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

from frontend.views import visualize_foosball
from backend import data_models, data_read_in

logger = logging.getLogger(__name__)

def main() -> None:
    visualize_foosball()

DATA = Path(r"C:\Users\miles\OneDrive\Documents\coding\foosball_data\data")

def test():
    with (DATA / "models/input.json").open('r', encoding='utf-8') as f:
        data_spec_raw = json.load(f)

    game_spec = data_models.DataSpecification.model_validate(data_spec_raw)

    game_options = data_read_in.read_in_games_options()
    try:
        games = data_models.read_in_data(game_options[0].url, game_spec.fields)
    except:
        games = data_read_in.read_in_games_from_csv()
    logger.info("Initial shape: %s", games.shape)
    games, invalid = game_spec.check_data(games)
    for i in invalid:
        logger.info(i.get_message())
    logger.info("Final shape: %s", games.shape)

if __name__ == "__main__":
    #main()
    test()
