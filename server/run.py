import os
import sys
import tomllib

from src import start_server

DEFAULT_CONFIG_PATH = "config.toml"

if __name__ == "__main__":
    config_path = DEFAULT_CONFIG_PATH

    # optionally get config path from args
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        if not os.path.exists(config_path):
            print(f"Config file not found: {config_path}")
            sys.exit(1)
        print(f"Using config file: {config_path}")

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    start_server(config)
