from datetime import datetime
import json
from typing import TypedDict
import os
from src.tag import Tag, get_tag_by_id
from src.utils import note_exists, is_valid_filename, get_default_note_title
from src import NOTES_DIR


class ValidationError(Exception):
    pass


class SerializedNote(TypedDict):
    """A type representing a serialized note."""

    id: int
    content: str
    title: str
    created: float
    last_modified: float
    last_opened: float
    audio_file: str
    summary: str
    tag_ids: list[int]


class Note:
    """
    A class representing a note. It has a title, content, and metadata such as
    creation and modification times.
    It can be serialized to and deserialized from JSON.
    It can also be saved to and loaded from a file.
    """

    def __init__(self, audio_file=None) -> None:
        """Create a new note with default values."""
        now = datetime.now()
        self._id = int(now.timestamp() * 1e6)
        self._content = ""
        self._title = get_default_note_title(NOTES_DIR, "New note")
        self.created = now
        self.last_modified = now
        self.last_opened = now
        self.last_save_location = None
        self._audio_file: str | None = audio_file
        self._summary: str = ""
        self._tags: set[Tag] = set()

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if self._title == value:
            return
        if not is_valid_filename(f"{value}.note"):
            raise ValidationError(f"{value} is not a valid filename")
        elif note_exists(NOTES_DIR, value):
            raise ValueError(f"a note named {value} already exists")
        self._title = value
        self.last_modified = datetime.now()
        self.save()

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if self._content != value:
            self._content = value
            self.last_modified = datetime.now()
            self.save()

    @property
    def audio_file(self):
        return self._audio_file

    @audio_file.setter
    def audio_file(self, value):
        self._audio_file = value
        self.last_modified = datetime.now()
        self.save()

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        self._summary = value
        self.last_modified = datetime.now()
        self.save()

    @property
    def tags(self):
        return self._tags

    def add_tag(self, tag: Tag):
        if tag not in self._tags:
            self._tags.add(tag)
            self.last_modified = datetime.now()
            self.save()

    def remove_tag(self, tag: Tag):
        if tag in self._tags:
            self._tags.remove(tag)
            self.last_modified = datetime.now()
            self.save()

    def serialize(self) -> SerializedNote:
        """Serialize the note to a JSON-compatible dictionary."""
        return {
            "id": self._id,
            "content": self.content,
            "title": self.title,
            "created": self.created.timestamp(),
            "last_modified": self.last_modified.timestamp(),
            "last_opened": self.last_opened.timestamp(),
            "audio_file": self._audio_file or "",
            "summary": self._summary,
            "tag_ids": [tag.id for tag in self._tags],
        }

    def load_from_serialized(self, sn: SerializedNote):
        """Load the note from a serialized note."""
        self._id = sn["id"]
        self._content = sn["content"]
        self._title = sn["title"]
        self.created = datetime.fromtimestamp(sn["created"])
        self.last_modified = datetime.fromtimestamp(sn["last_modified"])
        self.last_opened = datetime.fromtimestamp(sn["last_opened"])
        self._audio_file = sn["audio_file"] or None
        self._summary = sn["summary"]
        # be careful not to load tags that have been deleted
        tags_or_none = [get_tag_by_id(tag_id) for tag_id in sn["tag_ids"]]
        self._tags = set([tag for tag in tags_or_none if tag is not None])

    def save(self):
        """
        Save the note to a file.
        - If the note has not been saved before, it is saved to a new file.
        - If the note has been saved before, it is saved to the same file.
        - If the note has been saved before but the title has changed since the last save,
        the old file is deleted and the note is saved to a new file.
        """
        outfile = os.path.join(NOTES_DIR, f"{self.title}.note")
        with open(outfile, "w+") as f:
            s = json.dumps(self.serialize(), indent=4)
            f.write(s)
        if self.last_save_location is not None and self.last_save_location != outfile:
            os.remove(self.last_save_location)
        self.last_save_location = outfile

    def delete(self):
        """Delete the note from the filesystem."""
        if self.last_save_location is not None:
            os.remove(self.last_save_location)
        if self._audio_file is not None:
            os.remove(self._audio_file)


def load_note(fname, dir=NOTES_DIR) -> Note:
    """Load a note from a file."""
    n = Note()
    filepath = os.path.join(dir, fname)
    with open(filepath) as f:
        serialized_note = json.loads(f.read())
        n.load_from_serialized(serialized_note)
        n.last_save_location = filepath
    return n


def load_notes(
    dir=NOTES_DIR,
) -> list[Note]:
    """Load all notes from a directory."""
    notes = []
    for path, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".note"):
                notes.append(load_note(file))
        break  # TODO add folder support
    return notes
