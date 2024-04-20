import numpy as np
from ollama import Client as OllamaClient, Message, Options
import requests
from typing import Literal, Sequence

from . import CONFIG
from .note import Note


ollama_url = f"http://{CONFIG['ollama']['host']}:{CONFIG['ollama']['port']}"
LLM = OllamaClient(ollama_url)


class OllamaConversation:
    def __init__(
        self,
        model=CONFIG["ollama"]["frontend"]["chat_model"],
        system_message: str | None = None,
    ):
        self.model = model
        self.messages: list[Message] = []
        if system_message:
            self.add_message("system", system_message)

    def add_message(self, role: Literal["system", "user", "assistant"], content: str):
        self.messages.append({"role": role, "content": content})

    def get_response(self) -> str:
        LLM.pull(self.model)
        response = LLM.chat(self.model, self.messages, options=Options(num_ctx=32768))
        message: Message = response["message"]  # type: ignore
        self.messages.append(message)
        return message["content"]


def summarize_note(note: Note) -> str:
    conversation = OllamaConversation(
        system_message="You are a language model that summarizes text."
    )
    conversation.add_message(
        "user",
        f"Please summarize the following text (enclosed in triple quotes) in a sentence or two. Don't say 'here is the summary' or anything like that, just respond with the summary itself. Here is the text: '''{note.content}'''",
    )
    return conversation.get_response()


def start_conversation_about_note(note: Note) -> OllamaConversation:
    conversation = OllamaConversation(
        system_message="You are a language model that can answer questions about text."
    )
    conversation.add_message(
        "user", f"Consider the following text: '''{note.content}'''"
    )
    return conversation


def get_embedding(text: str) -> Sequence[float]:
    return LLM.embeddings(
        model=CONFIG["ollama"]["frontend"]["embed_model"], prompt=text
    )[
        "embedding"
    ]  # type: ignore


def update_note_embedding(note: Note):
    new_embedding = get_embedding(note.content)
    note.embedding = list(new_embedding)


def compare_embeddings(emb_1: Sequence[float], emb_2: Sequence[float]) -> float:
    return np.dot(emb_1, emb_2) / (np.linalg.norm(emb_1) * np.linalg.norm(emb_2))


def transcribe_wav(wav_file: str) -> str:
    endpoint = (
        f"http://{CONFIG['whisper']['host']}:{CONFIG['whisper']['port']}/inference"
    )
    try:
        response = requests.post(
            endpoint,
            files={"file": ("audio.wav", open(wav_file, "rb"), "audio/wav")},
            data={
                "temperature": "0.0",
                "temperature_inc": "0.2",
                "response_format": "json",
            },
        )
        response.raise_for_status()
        return response.json()["text"]
    except Exception as e:
        # TODO how to handle exceptions?
        raise e
