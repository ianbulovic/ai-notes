from .. import get_server
from ..db_model import Note, Tag, Media

app = get_server().app
chromadb_client = get_server().chromadb_client
ollama_client = get_server().ollama_client
whisper_client = get_server().whisper_client


def get_db_health():
    try:
        Note.query.first()
        Tag.query.first()
        Media.query.first()
        return "UP"
    except Exception as e:
        print(e)
        return "DOWN"


@app.route("/api/health", methods=["GET"])
def health():
    return {
        "status": "UP",
        "checks": {
            "db": get_db_health(),
            "chromadb": chromadb_client.alive(),
            "ollama": ollama_client.alive(),
            "whisper": whisper_client.alive(),
        },
    }
