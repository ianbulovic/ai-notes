import tempfile
import chromadb
import io
from ollama import Client as _OllamaClient
import os
import requests
import subprocess
import sys
import time
from typing import Any, Mapping, Sequence

__all__ = [
    "ChromadbBackend",
    "ChromadbClient",
    "OllamaBackend",
    "OllamaClient",
    "WhisperBackend",
    "WhisperClient",
    "BackendManager",
]

### ChromaDB ###


class ChromadbClient:
    def __init__(self, config):
        self.host = config["host"]
        self.port = config["port"]
        self.client = chromadb.HttpClient(host=self.host, port=self.port)
        self.collection = self.client.create_collection(
            name="notes", get_or_create=True
        )

    def add(self, ids: list[str], docs: list[str], embeddings: list[Sequence[float]]):
        self.collection.upsert(ids=ids, documents=docs, embeddings=embeddings)

    def remove(self, ids: list[str]):
        self.collection.delete(ids=ids)

    def clear(self):
        self.client.delete_collection("notes")
        self.collection = self.client.create_collection("notes")

    def query(
        self, query_embedding: Sequence[float], n_results: int = 10
    ) -> list[tuple[int, float]]:
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["distances"],
        )
        ids: list[int] = [int(id) for id in result["ids"][0]]
        distances: list[float] = result["distances"][0]  # type: ignore
        return list(zip(ids, distances))

    def get(self, id: str) -> Sequence[float] | None:
        hit = self.collection.get(id)["embeddings"]
        return hit[0] if hit else None

    def alive(self):
        try:
            self.client.heartbeat()
            return True
        except Exception:
            return False


class ChromadbBackend:
    def __init__(self, config):
        self.host = config["host"]
        self.port = config["port"]
        self.name = "chromadb"

    def start(self):
        self.process = subprocess.Popen(
            [
                # fmt: off
                sys.executable, "-m", "chromadb.cli.cli", "run", 
                "--path", "./instance", 
                "--host", self.host, 
                "--port", f"{self.port}",
                # fmt: on
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def stop(self):
        self.process.terminate()

    def alive(self):
        try:
            requests.get(f"http://{self.host}:{self.port}/api/v1").raise_for_status()
            return True
        except Exception:
            return False


### Ollama ###


class OllamaClient:
    def __init__(self, config):
        self.config = config
        self.client = _OllamaClient(f"{config['host']}:{config['port']}")
        self.chat_model = config["chat_model"]
        self.embed_model = config["embed_model"]
        self.client.pull(self.chat_model)
        self.client.pull(self.embed_model)

    def chat(self, messages: list[Mapping[str, Any]]) -> Mapping[str, Any]:
        return self.client.chat(self.chat_model, messages)  # type: ignore

    def embed(self, text: str) -> Sequence[float]:
        return self.client.embeddings(self.embed_model, prompt=text)["embedding"]  # type: ignore

    def alive(self):
        try:
            self.client.list()
            return True
        except Exception:
            return False


class OllamaBackend:
    def __init__(self, config):
        self.host = config["host"]
        self.port = config["port"]
        self.executable = config["executable"]
        self.name = "ollama"

    def start(self):
        self.process = subprocess.Popen(
            [self.executable, "serve"],
            env={
                "OLLAMA_HOST": f"{self.host}:{self.port}",
                "HOME": os.environ["HOME"],
            },
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def stop(self):
        self.process.terminate()

    def alive(self):
        try:
            requests.get(f"http://{self.host}:{self.port}").raise_for_status()
            return True
        except Exception:
            return False


### Whisper ###


class WhisperClient:
    def __init__(self, config):
        self.endpoint = f"http://{config['host']}:{config['port']}"

    def transcribe(self, file_path: str):
        # check if file is webm
        if file_path.endswith(".webm"):
            # convert to wav with 16khz sample rate
            with tempfile.NamedTemporaryFile(suffix=".wav") as f:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        file_path,
                        "-ar",
                        "16000",
                        f.name,
                    ],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                return self._transcribe(f.name)

    def _transcribe(self, wav_path: str):
        response = requests.post(
            f"{self.endpoint}/inference",
            files={"file": ("audio.wav", open(wav_path, "rb"), "audio/wav")},
            data={
                "temperature": "0.0",
                "temperature_inc": "0.2",
                "response_format": "json",
            },
        )
        response.raise_for_status()
        return response.json()["text"]

    def alive(self):
        requests.get(self.endpoint).raise_for_status()
        return True


class WhisperBackend:
    def __init__(self, config):
        self.host = config["host"]
        self.port = config["port"]
        self.model = config["model"]
        self.executable = config["executable"]
        self.name = "whisper"

    def start(self):
        self.process = subprocess.Popen(
            [
                # fmt: off
                self.executable,
                "-m", self.model,
                "--host", self.host,
                "--port", f"{self.port}",
                # fmt: on
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def stop(self):
        self.process.terminate()

    def alive(self):
        try:
            requests.get(f"http://{self.host}:{self.port}").raise_for_status()
            return True
        except Exception:
            return False


### Backend Manager ###


class BackendManager:

    def __init__(self, config):
        self.chromadb = ChromadbBackend(config["chromadb"])
        self.ollama = OllamaBackend(config["ollama"])
        self.whisper = WhisperBackend(config["whisper"])

    def __enter__(self):
        self.chromadb.start()
        self.ollama.start()
        self.whisper.start()
        for backend in [self.chromadb, self.ollama, self.whisper]:
            for _ in range(50):
                if backend.alive():
                    break
                time.sleep(0.2)
            else:
                raise Exception(f"Failed to start {backend.name}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.chromadb.stop()
        self.ollama.stop()
        self.whisper.stop()
        return False
