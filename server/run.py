import sys
import tomllib
from src import start_server


if __name__ == "__main__":
    config_path = "config.toml"

    # optionally get config path from args
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    start_server(config)
