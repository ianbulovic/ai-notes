from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
from flask_cors import CORS

from .backends import ChromadbClient, OllamaClient, WhisperClient, BackendManager


class Server:
    """The main server class. This class handles configuration and running of the server and the backends."""

    def __init__(self, config):
        self.config = config
        self.app = Flask(__name__)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = config["database"]["uri"]
        self.app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["SECRET_KEY"] = "super secret key"

        CORS(self.app)
        self.db = SQLAlchemy(self.app, engine_options={"poolclass": NullPool})

    def run(self):
        """Spin up the backends and start the server."""
        with BackendManager(self.config):
            self.chromadb_client = ChromadbClient(self.config["chromadb"])
            self.ollama_client = OllamaClient(self.config["ollama"])
            self.whisper_client = WhisperClient(self.config["whisper"])

            # Expose the routes for the api
            from . import routes

            # Make sure the database is created and all notes are embedded
            with self.app.app_context():
                self.db.create_all()
                self.ensure_embedded()

            # Start the server
            self.app.run(
                host=self.config["api"]["host"],
                port=self.config["api"]["port"],
                debug=self.config["settings"]["debug"],
            )

    def ensure_embedded(self):
        """Ensure that all notes are embedded in the ChromaDB database."""

        # Import Note here to avoid circular import with db_model
        from .db_model import Note

        regenerate_embeddings = self.config["settings"]["regenerate_embeddings"]
        if regenerate_embeddings:
            print("Clearing all embeddings")
            self.chromadb_client.clear()

        ids = []
        docs = []
        embeddings = []
        for note in Note.query.all():
            if regenerate_embeddings or self.chromadb_client.get(str(note.id)) is None:
                ids.append(str(note.id))
                doc = f"{note.title}\n{note.content}"
                docs.append(doc)
                embeddings.append(self.ollama_client.embed(doc))
                print(f"Embedded note {note.id} ({note.title})")
        if ids:
            self.chromadb_client.add(ids, docs, embeddings)


_server: Server | None = None
"""The server instance."""


def start_server(config):
    """Start the server with the given configuration."""
    global _server
    _server = Server(config)
    _server.run()


def get_server():
    """Get the server instance."""
    global _server
    if _server is None:
        raise Exception("Cannot access server before it has been started.")
    return _server
