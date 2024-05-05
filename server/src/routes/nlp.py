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


# Routes for note embedding


@app.route("/api/embed/<int:note_id>", methods=["POST"])
def update_note_embedding(note_id):
    note = Note.query.get_or_404(note_id)
    doc = f"{note.title}\n{note.content}"
    embedding = ollama_client.embed(doc)
    chromadb_client.add([str(note.id)], [doc], [embedding])
    return note.to_dict()


# Routes for RAG


@app.route("/api/rag", methods=["POST"])
def rag():
    data = request.json
    if data is None or "query" not in data:
        return {"error": "Invalid request"}, 400
    query = data["query"]
    n_results = data.get("nResults", 10)
    query_embedding = ollama_client.embed(query)
    ids, distances = chromadb_client.query(query_embedding, n_results=n_results)
    notes = Note.query.filter(Note.id.in_(ids)).all()

    messages = [
        {
            "role": "system",
            "content": """You are an AI assistant that retrieves notes based on user queries. 
            You will be given a query and a list of notes. You need to select which notes (if any) are relevant to the query.
            Each note has a title, content, and an ID. Please provide your response as a comma-separated list of note IDs that are relevant to the query.
            For example, if notes with IDs 1, 2, and 3 are relevant, your response should be "1, 2, 3". If no notes are relevant, respond with "None".
            Do not say anything else in your response, or the user will not be able to parse it.""",
        },
        {
            "role": "user",
            "content": f"""Here is my query: "{query}" 
            Here are the notes to analyze:
            {"\n\n".join([f"Note ID: {note.id}\n    Title: {note.title}\n    Content: {note.content}" for note in notes])}
            
            
            Now please consider the notes above and provide a list of comma-separated note IDs relevant to the query "{query}", or "None" if no notes are relevant. Do not say anything else in your response.""",
        },
    ]
    print(f"Query: {query}")
    print(f"Messages: {messages}")
    response = ollama_client.chat(messages)
    content = response["message"]["content"]
    print(f"Response: {content}")

    try:
        if content.lower() == "none":
            notes = []
        else:
            note_ids = [int(id) for id in content.split(",")]
            print(f"Parsed list of IDs: {note_ids}")
            notes = Note.query.filter(Note.id.in_(note_ids)).all()
    except Exception as e:
        print(f"Error extracting note IDs from response '{content}'")

    # print(f"Resulting Notes: {[note.to_dict() for note in notes]}")

    return {"notes": [note.to_dict() for note in notes]}


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
