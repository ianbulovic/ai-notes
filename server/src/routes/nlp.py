import os
from flask import request

from .. import get_server
from ..db_model import Note, Media


app = get_server().app
db = get_server().db
chromadb_client = get_server().chromadb_client
ollama_client = get_server().ollama_client
whisper_client = get_server().whisper_client
config = get_server().config

# Routes for llm


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    if data is None or "messages" not in data:
        return {"error": "Invalid request"}, 400
    messages = data["messages"]
    response = ollama_client.chat(messages)
    return response["message"]


# @app.route("/api/embed", methods=["POST"])
# def embed():
#     data = request.json
#     if data is None or "text" not in data:
#         return {"error": "Invalid request"}, 400
#     input = data["text"]
#     response = {"embedding": ollama_client.embed(text=input)}
#     return response


@app.route("/api/embed/<int:note_id>", methods=["POST"])
def update_note_embedding(note_id):
    note = Note.query.get_or_404(note_id)
    doc = f"{note.title}\n{note.content}"
    embedding = ollama_client.embed(doc)
    chromadb_client.add([str(note.id)], [doc], [embedding])
    return note.to_dict()


# Routes for transcription


@app.route("/api/transcribe/<int:media_id>", methods=["POST"])
def transcribe(media_id: int):
    media = Media.query.get_or_404(media_id)
    media_path = os.path.join(os.getcwd(), config["api"]["media_path"], media.path)
    try:
        text = whisper_client.transcribe(media_path)
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}, 500
