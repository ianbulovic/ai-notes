from datetime import datetime
import json
import random
from typing import TypedDict

from src import NOTES_DIR, TAGS_FILE


def _generate_random_color() -> str:
    """Generate a random color in hex format."""
    return f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"


class SerializedTag(TypedDict):
    """A type representing a serialized tag."""

    id: int
    name: str
    color: str


class Tag:
    """A tag that can be assigned to notes."""

    def __init__(
        self, name: str = "New tag", color: str = _generate_random_color()
    ) -> None:
        self._id = int(datetime.now().timestamp() * 1e6)
        self._name = name
        self._color = color

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Tag) and value.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)

    def serialize(self) -> SerializedTag:
        """Serialize the tag to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
        }

    def load_from_serialized(self, serialized: SerializedTag) -> None:
        """Load the tag from a serialized dictionary."""
        self._id = serialized["id"]
        self._name = serialized["name"]
        self._color = serialized["color"]

    def save(self) -> None:
        """Save the tag to the tags file."""
        tags = load_tags()
        tags = [tag for tag in tags if tag.id != self.id]
        tags.append(self)
        with open(TAGS_FILE, "w") as file:
            json.dump(tags, file)


def load_tags() -> list[Tag]:
    """Load tags from the tags file."""
    with open(TAGS_FILE, "r") as file:
        tags = []
        for serialized in json.load(file):
            tag = Tag()
            tag.load_from_serialized(serialized)
            tags.append(tag)
        return tags


def get_tag_by_id(tag_id: int) -> Tag:
    """Get a tag by its ID."""
    for tag in load_tags():
        if tag.id == tag_id:
            return tag
    raise ValueError(f"No tag with ID {tag_id} found.")
