import datetime
from flask import request
import os
from sqlalchemy import func

from .. import get_server
from ..db_model import Note, Tag, Media

app = get_server().app
db = get_server().db
ollama_client = get_server().ollama_client
chromadb_client = get_server().chromadb_client

# Routes for notes


@app.route("/api/notes", methods=["GET"])
def get_notes():
    search_query = request.args.get("q")
    sort_mode = request.args.get("sort")
    tags = request.args.get("tags")
    results_per_page = int(request.args.get("n", 10))
    page = int(request.args.get("page", 1))

    # add a column for search score
    notes = Note.query

    if search_query:

        # Filter by search query
        notes = notes.filter(
            Note.title.ilike(f"%{search_query}%")
            | Note.content.ilike(f"%{search_query}%")
        )

        # TODO this is too slow, need to optimize
        # query the embeddings
        # query_embedding = ollama_client.embed(search_query)
        # matches = chromadb_client.query(query_embedding, n_results=1)
        # note_ids = [nid for nid, dist in matches]
        # notes = notes.union(Note.query.filter(Note.id.in_(note_ids)))

    if tags:
        tag_ids = [int(tag_id) for tag_id in tags.split(",")]
        for tag_id in tag_ids:
            notes = notes.filter(Note.tags.any(Tag.id == tag_id))

    if sort_mode == "created":
        notes = notes.order_by(Note.created_at.desc())
    elif sort_mode == "modified":
        notes = notes.order_by(Note.last_modified.desc())
    elif sort_mode == "opened":
        notes = notes.order_by(Note.last_opened.desc())
    elif sort_mode == "title":
        # ignore case when sorting by title
        notes = notes.order_by(func.lower(Note.title))
    elif search_query and sort_mode == "relevance":
        title_score = func.char_length(Note.title) - func.char_length(
            func.replace(func.lower(Note.title), func.lower(search_query), "")
        )
        content_score = func.char_length(Note.content) - func.char_length(
            func.replace(func.lower(Note.content), func.lower(search_query), "")
        )

        notes = notes.order_by(title_score.desc(), content_score.desc())

    pagination = notes.paginate(page=page, per_page=results_per_page, count=True)
    notes = pagination.items
    total_pages = pagination.pages
    return {"notes": [note.to_dict() for note in notes], "pages": total_pages}


@app.route("/api/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    note = Note.query.get_or_404(note_id)
    return note.to_dict()


@app.route("/api/notes", methods=["POST"])
def create_note():
    note = Note.new_note()
    db.session.add(note)
    db.session.commit()
    return note.to_dict(), 201


@app.route("/api/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    note = Note.query.get_or_404(note_id)
    data = request.json
    if data is not None:
        for key, value in data.items():
            if hasattr(note, key):
                setattr(note, key, value)
            else:
                return {"error": f"Invalid key '{key}'"}, 400
    note.last_modified = func.now()
    db.session.commit()
    return note.to_dict()


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    chromadb_client.remove([str(note_id)])
    return "", 204


@app.route("/api/notes/<int:note_id>/open", methods=["POST"])
def open_note(note_id):
    note = Note.query.get_or_404(note_id)
    note.last_opened = func.now()
    db.session.commit()
    return note.to_dict()


# Routes for tags


@app.route("/api/tags", methods=["GET"])
def get_tags():
    tags = Tag.query.all()
    return {"tags": [tag.to_dict() for tag in tags]}


@app.route("/api/tags/<int:tag_id>", methods=["GET"])
def get_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return tag.to_dict()


@app.route("/api/tags", methods=["POST"])
def create_tag():
    data = request.json
    if not data or "name" not in data or "color" not in data:
        return {"error": "Missing required fields"}, 400
    tag = Tag.new_tag(data["name"], data["color"])
    db.session.add(tag)
    db.session.commit()
    return tag.to_dict(), 201


@app.route("/api/tags/<int:tag_id>", methods=["PUT"])
def update_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    data = request.json
    if data is not None:
        for key, value in data.items():
            if hasattr(tag, key):
                setattr(tag, key, value)
            else:
                return {"error": f"Invalid key '{key}'"}, 400
    db.session.commit()
    return tag.to_dict()


@app.route("/api/tags/<int:tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return "", 204


# Routes for notes-tags relationship


@app.route("/api/notes/<int:note_id>/tags", methods=["GET"])
def get_note_tags(note_id):
    note = Note.query.get_or_404(note_id)
    return {"tags": [tag.to_dict() for tag in note.tags]}


@app.route("/api/notes/<int:note_id>/tags/<int:tag_id>", methods=["POST"])
def add_tag_to_note(note_id, tag_id):
    note = Note.query.get_or_404(note_id)
    tag = Tag.query.get_or_404(tag_id)
    if tag in note.tags:
        return note.to_dict()
    note.tags.append(tag)
    db.session.commit()
    return note.to_dict()


@app.route("/api/notes/<int:note_id>/tags/<int:tag_id>", methods=["DELETE"])
def remove_tag_from_note(note_id, tag_id):
    note = Note.query.get_or_404(note_id)
    tag = Tag.query.get_or_404(tag_id)
    if tag not in note.tags:
        return note.to_dict()
    note.tags.remove(tag)
    db.session.commit()
    return note.to_dict()


@app.route("/api/tags/<int:tag_id>/notes", methods=["GET"])
def get_tag_notes(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    notes = Note.query.filter(Note.tags.contains(tag)).all()
    return {"notes": [note.to_dict() for note in notes]}


# Routes for media


@app.route("/api/media", methods=["POST"])
def upload_media():
    if "webm" not in request.files:
        return {"error": "No file part"}, 400

    file_storage = request.files["webm"]

    os.makedirs("media", exist_ok=True)
    save_path = f"media/{datetime.datetime.now().isoformat()}.webm"
    file_storage.save(save_path)

    media = Media.new_media(save_path)

    db.session.add(media)
    db.session.commit()
    return {"id": media.id}


# Routes for notes-media relationship


@app.route("/api/notes/<int:note_id>/media/<int:media_id>", methods=["POST"])
def add_media_to_note(note_id, media_id):
    note = Note.query.get_or_404(note_id)
    media = Media.query.get_or_404(media_id)
    if media in note.media:
        return note.to_dict()
    note.media.append(media)
    db.session.commit()
    return note.to_dict()
