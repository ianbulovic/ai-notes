from datetime import datetime
import json
from typing import TypedDict
from src.utils import generate_random_hex_color

from src import TAGS_FILE


class SerializedTag(TypedDict):
    """A type representing a serialized tag."""

    id: int
    name: str
    color: str


class Tag:
    """A tag that can be assigned to notes."""

    def __init__(
        self, name: str = "New tag", color: str = "#FF0000", save=True
    ) -> None:
        self._id = int(datetime.now().timestamp() * 1e6)
        self._name = name
        self._color = color
        if save:
            self.save()

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.save()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.save()

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
            json.dump([t.serialize() for t in tags], file)

    def foreground_color(self) -> str:
        """Get the foreground color for the tag."""
        # TODO blindly trusting copilot on this one for now
        r, g, b = [int(self.color[i : i + 2], 16) for i in (1, 3, 5)]
        luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
        return "#000000" if luma > 128 else "#ffffff"

    def as_html_span(self, additional_style: str = "") -> str:
        """Get an HTML span element representing the tag."""
        return f'<span class="tag" style="background-color: {self.color}; color: {self.foreground_color()}; white-space: nowrap; padding: 0.2rem 0.5rem; border-radius: 0.5rem; {additional_style}">{self.name}</span>'


def load_tags() -> list[Tag]:
    """Load tags from the tags file."""
    with open(TAGS_FILE, "r") as file:
        tags = []
        for serialized in json.load(file):
            tag = Tag(save=False)
            tag.load_from_serialized(serialized)
            tags.append(tag)
        return sorted(tags, key=lambda t: t.name)


def get_tag_by_id(tag_id: int) -> Tag | None:
    """Get a tag by its ID."""
    for tag in load_tags():
        if tag.id == tag_id:
            return tag
    return None


def delete_tag(tag: Tag) -> None:
    """Delete a tag."""
    tags = load_tags()
    tags = [t for t in tags if t.id != tag.id]
    with open(TAGS_FILE, "w") as file:
        json.dump([t.serialize() for t in tags], file)
