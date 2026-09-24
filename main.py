import cli
from config import Config
from controller import Controller


def main() -> None:
    config: Config = cli.cli_to_config()


    app: Controller = Controller(config)
    app.run()

if __name__ == "__main__":
    main()