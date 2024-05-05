from . import get_server
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = get_server().app
db = get_server().db


class NoteTag(db.Model):
    note_id = db.Column(db.Integer, db.ForeignKey("note.id"), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"), primary_key=True)


class NoteMedia(db.Model):
    note_id = db.Column(db.Integer, db.ForeignKey("note.id"), primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey("media.id"), primary_key=True)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    last_modified = db.Column(db.DateTime, nullable=False)
    last_opened = db.Column(db.DateTime, nullable=True)
    tags = db.relationship("Tag", secondary="note_tag", backref="notes")
    media = db.relationship("Media", secondary="note_media", backref="notes")

    @classmethod
    def new_note(cls):
        note = cls()
        if not db.session.query(cls.id).count():
            note.id = 1
        else:
            note.id = db.session.query(db.func.max(cls.id)).scalar() + 1
        default_title = "Untitled Note"
        # if the default title already exists, append a number to it until it's unique
        title = default_title
        i = 1
        while cls.query.filter_by(title=title).first():
            title = f"{default_title} {i}"
            i += 1
        note.title = title
        note.content = ""
        note.created_at = note.last_modified = note.last_opened = db.func.now()
        return note

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
            "last_opened": self.last_opened,
            "tags": [tag.to_dict() for tag in self.tags],  # type: ignore
            "media": [media.id for media in self.media],  # type: ignore
        }


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    color = db.Column(db.String(7), nullable=False)

    @classmethod
    def new_tag(cls, name: str, color: str):
        tag = cls()
        if not db.session.query(cls.id).count():
            tag.id = 1
        else:
            tag.id = db.session.query(db.func.max(cls.id)).scalar() + 1
        tag.name = name
        tag.color = color
        return tag

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
        }


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(255), nullable=False)

    @classmethod
    def new_media(cls, path: str):
        media = cls()
        if not db.session.query(cls.id).count():
            media.id = 1
        else:
            media.id = db.session.query(db.func.max(cls.id)).scalar() + 1
        media.path = path
        return media

    def to_dict(self):
        return {
            "id": self.id,
        }


class NoteView(ModelView):
    column_list = (
        "title",
        "content",
        "created_at",
        "last_modified",
        "last_opened",
        "tags",
        "media",
    )
    column_searchable_list = ("title", "content")
    column_filters = ("created_at", "last_modified", "last_opened")
    column_sortable_list = ("title", "created_at", "last_modified", "last_opened")
    column_default_sort = ("last_modified", True)
    form_columns = ("title", "content", "tags", "media")
    form_ajax_refs = {
        "tags": {"fields": (Tag.name,)},
        "media": {"fields": (Media.path,)},
    }


admin = Admin(app, name="Notes", template_mode="bootstrap3")
admin.add_view(NoteView(Note, db.session))
admin.add_view(ModelView(Tag, db.session))
admin.add_view(ModelView(Media, db.session))


# from .. import chromadb_client, ollama_client, config

# ids: list[str] = []
# docs: list[str] = []
# embeddings: list[Sequence[float]] = []
# for note in Note.query.all():
#     model = config["ollama"]["embed_model"]
#     emb = ollama_client.embeddings(model, prompt=note.content)
#     ids.append(str(note.id))
#     docs.append(note.content)
#     embeddings.append(emb)

# chromadb_client.add(ids, docs, embeddings)
