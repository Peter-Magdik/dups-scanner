import logging
import sys

import cli
import constants
from config import Config
from controller import Controller

logger: logging.Logger = logging.getLogger(name=__name__)


def main() -> None:
    config: Config = cli.cli_to_config()

    app: Controller = Controller(config)
    app.run()
    logger.info(msg="App ran successfully")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception(msg="Unexpected error")
        sys.exit(constants.EXIT_UNEXPECTED)
