import cli
from controller import Controller

def main():
    config = cli.cli_to_config()


    app = Controller(config)
    app.run()

if __name__ == "__main__":
    main()