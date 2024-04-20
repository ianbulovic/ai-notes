import logging
import os
import signal
import subprocess
import threading
import time
import tomllib
from typing import IO


class Server:
    def __init__(self, config_file: str):
        with open(config_file, "rb") as f:
            self.config = tomllib.load(f)
        self.processes: dict[str, subprocess.Popen] = {}

    def serve_whisper_backend(self):
        executable = self.config["whisper"]["backend"]["executable"]
        model_file = self.config["whisper"]["backend"]["model"]
        host = self.config["whisper"]["host"]
        port = self.config["whisper"]["port"]
        process = subprocess.Popen(
            [
                # fmt: off
                executable,
                "-m", model_file,
                "--host", host,
                "--port", f"{port}",
                # fmt: on
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.processes["whisper"] = process
        self.start_logging_threads("whisper", process)

    def serve_ollama_backend(self):
        executable = self.config["ollama"]["backend"]["executable"]
        host = self.config["ollama"]["host"]
        port = self.config["ollama"]["port"]
        process = subprocess.Popen(
            [executable, "serve"],
            env={
                "OLLAMA_HOST": f"{host}:{port}",
                "HOME": os.environ["HOME"],
            },
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.processes["ollama"] = process
        self.start_logging_threads("ollama", process)

    def start_logging_threads(self, process_name: str, process: subprocess.Popen):
        logger = logging.getLogger(process_name)
        logger.info(f"backend started with PID {process.pid}")

        def log_output(io: IO, level: int):
            for line in io:
                logger.log(level, line.decode().strip())

        out_thread = threading.Thread(
            target=log_output,
            args=(process.stdout, logging.INFO),
            name=f"{process_name}-out-logger",
        )
        out_thread.start()

        err_thread = threading.Thread(
            target=log_output,
            args=(process.stderr, logging.ERROR),
            name=f"{process_name}-err-logger",
        )
        err_thread.start()

    def __enter__(self):
        logging.info("starting server...")
        self.serve_whisper_backend()
        self.serve_ollama_backend()
        logging.info("server started, all backends are running")
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        for process_name, process in self.processes.items():
            process.send_signal(signal.SIGINT)
            process.wait()
            logging.getLogger(process_name).info(
                f"backend stopped with return code {process.returncode}"
            )
        self.processes = {}
        logging.info("server stopped.")


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    with Server(config_file="config.toml"):
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
