import datetime
from flask import request, send_from_directory
import os
from sqlalchemy import func

from .. import get_server
from ..db_model import Note, Tag, Media

app = get_server().app
db = get_server().db
config = get_server().config
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

    notes = Note.query

    if tags:
        tag_ids = [int(tag_id) for tag_id in tags.split(",")]
        for tag_id in tag_ids:
            notes = notes.filter(Note.tags.any(Tag.id == tag_id))

    if search_query:

        # Filter by search query
        # notes = notes.filter(
        #     Note.title.ilike(f"X%{search_query}%")
        #     | Note.content.ilike(f"X%{search_query}%")
        # )

        title_matches = Note.query.filter(Note.title.ilike(f"%{search_query}%"))
        title_score = func.char_length(Note.title) - func.char_length(
            func.replace(func.lower(Note.title), func.lower(search_query), "")
        )

        content_matches = Note.query.filter(Note.content.ilike(f"%{search_query}%"))
        content_score = func.char_length(Note.content) - func.char_length(
            func.replace(func.lower(Note.content), func.lower(search_query), "")
        )
        notes = title_matches.union(content_matches).distinct()

        # TODO this is too slow and too inaccurate
        # query the embeddings
        # query_embedding = ollama_client.embed(search_query)
        # ids, distances = chromadb_client.query(query_embedding, n_results=20)
        # distance_map = dict(zip(ids, distances))
        # if len(ids) > 0:
        #     semantic_matches = Note.query.filter(Note.id.in_(ids))
        #     # calculate semantic score using distance map, notes not in distance map = 0 score
        #     semantic_score = case(distance_map, value=Note.id, else_=1000)
        #     notes = notes.union(semantic_matches).distinct()
        #     if sort_mode == "relevance":
        #         notes = notes.order_by(
        #             title_score.desc(), content_score.desc(), semantic_score.asc()
        #         )
        # elif sort_mode == "relevance":
        #     notes = notes.order_by(title_score.desc(), content_score.desc())
        if sort_mode == "relevance":
            notes = notes.order_by(title_score.desc(), content_score.desc())

    if sort_mode == "created":
        notes = notes.order_by(Note.created_at.desc())
    elif sort_mode == "modified":
        notes = notes.order_by(Note.last_modified.desc())
    elif sort_mode == "opened":
        notes = notes.order_by(Note.last_opened.desc())
    elif sort_mode == "title":
        # ignore case when sorting by title
        notes = notes.order_by(func.lower(Note.title))

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


@app.route("/api/media/<int:media_id>", methods=["GET"])
def get_media(media_id):
    media = Media.query.get_or_404(media_id)
    media_dir = os.path.join(os.getcwd(), config["api"]["media_path"])
    return send_from_directory(media_dir, media.path)


@app.route("/api/media", methods=["POST"])
def upload_media():
    if "webm" not in request.files:
        return {"error": "No file part"}, 400

    file_storage = request.files["webm"]

    media_dir = config["api"]["media_path"]
    os.makedirs("media", exist_ok=True)

    filename = f"{int(datetime.datetime.now().timestamp() * 1000)}.webm"
    save_path = os.path.join(os.getcwd(), media_dir, filename)
    file_storage.save(save_path)

    media = Media.new_media(filename)

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
