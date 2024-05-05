from abc import ABC
import tempfile
import chromadb
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


class Backend(ABC):
    """Abstract base class for backend services."""

    name: str
    """The name of the backend service."""

    host: str
    """The host of the backend service."""

    port: int
    """The port of the backend service."""

    def start(self) -> None:
        """Start the backend service."""
        raise NotImplementedError

    def stop(self) -> None:
        """Stop the backend service."""
        raise NotImplementedError

    @classmethod
    def _alive(cls, host: str, port: int) -> bool:
        """Check if the backend service is running."""
        raise NotImplementedError

    def alive(self) -> bool:
        """Check if the backend service is running."""
        return self._alive(self.host, self.port)


### ChromaDB ###


class ChromadbClient:
    def __init__(self, config):
        self.host = config["host"]
        self.port = config["port"]
        self.client = chromadb.HttpClient(
            host=self.host,
            port=self.port,
        )

        self.collection_name = "note-content"
        self.embedding_function = None
        self.metadata = {"hnsw:space": "l2"}
        self.collection = self.client.create_collection(
            name=self.collection_name,
            get_or_create=True,
            embedding_function=self.embedding_function,
            metadata=self.metadata,
        )

    def add(self, ids: list[str], docs: list[str], embeddings: list[Sequence[float]]):
        self.collection.upsert(ids=ids, documents=docs, embeddings=embeddings)

    def remove(self, ids: list[str]):
        self.collection.delete(ids=ids)

    def clear(self):
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata=self.metadata,
        )

    def query(
        self,
        query_embedding: Sequence[float],
        n_results: int = 10,
        max_distance: float | None = None,
    ) -> tuple[list[int], list[float]]:
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["distances"],
        )
        ids: list[int] = []
        distances: list[float] = []
        for id, distance in zip(result["ids"][0], result["distances"][0]):  # type: ignore
            if max_distance is not None and distance > max_distance:
                break
            print(f"ID: {id}, Distance: {distance}")
            ids.append(int(id))
            distances.append(distance)
        return ids, distances

    def get(self, id: str) -> Sequence[float] | None:
        hit = self.collection.get(id, include=["embeddings"])["embeddings"]
        return hit[0] if hit else None

    def alive(self):
        try:
            self.client.heartbeat()
            return True
        except Exception:
            return False


class ChromadbBackend(Backend):

    def __init__(self, config):
        self.name = "chromadb"
        self.host = config["host"]
        self.port = config["port"]

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

    @classmethod
    def _alive(cls, host: str, port: int):
        try:
            requests.get(f"http://{host}:{port}/api/v1").raise_for_status()
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

    def chat(self, messages: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        return self.client.chat(self.chat_model, messages, options={"num_predict": 1024})  # type: ignore

    def embed(self, text: str) -> Sequence[float]:
        return self.client.embeddings(self.embed_model, prompt=text)["embedding"]  # type: ignore

    def alive(self):
        try:
            self.client.list()
            return True
        except Exception:
            return False


class OllamaBackend(Backend):
    def __init__(self, config):
        self.name = "ollama"
        self.host = config["host"]
        self.port = config["port"]
        self.executable = config["executable"]

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

    @classmethod
    def _alive(cls, host: str, port: int):
        try:
            requests.get(f"http://{host}:{port}").raise_for_status()
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


class WhisperBackend(Backend):
    def __init__(self, config):
        self.name = "whisper"
        self.host = config["host"]
        self.port = config["port"]
        self.model = config["model"]
        self.executable = config["executable"]

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

    @classmethod
    def _alive(cls, host: str, port: int):
        try:
            requests.get(f"http://{host}:{port}").raise_for_status()
            return True
        except Exception:
            return False


### Backend Manager ###


class BackendManager:

    def __init__(self, config):
        self.backends: list[Backend] = []
        self.external = []
        for name, backend in [
            ("chromadb", ChromadbBackend),
            ("ollama", OllamaBackend),
            ("whisper", WhisperBackend),
        ]:
            cfg = config[name]

            if cfg["external"]:
                self.external.append((backend, cfg["host"], cfg["port"], name))
            else:
                self.backends.append(backend(cfg))

    def __enter__(self):
        for backend in self.backends:
            backend.start()

        for backend in self.backends:
            for _ in range(50):
                if backend.alive():
                    break
                time.sleep(0.2)
            else:
                raise Exception(f"Failed to start {backend.name}")

        for backend, host, port, name in self.external:
            if not backend._alive(host, port):
                raise Exception(f"Failed to connect to {name}")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for backend in self.backends:
            backend.stop()
        return False
