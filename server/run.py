import tomllib
from src import start_server


if __name__ == "__main__":
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    start_server(config)
