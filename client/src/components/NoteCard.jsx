import { LinkContainer } from "react-router-bootstrap";
import "./NoteCard.css";
import { openNoteById } from "../api";
import { invertColor } from "../utils";
import NoteDeleteButton from "./NoteDeleteButton";

export default function NoteCard({ note, searchQuery, onDelete, showDelete }) {
  var displayTitle = <div>{note.title}</div>;
  var displayContent = (
    <div>
      {note.content.substring(0, 70)}
      {note.content.length > 70 ? "..." : ""}
    </div>
  );

  if (searchQuery) {
    const regex = new RegExp(searchQuery, "i");

    if (regex.test(note.title)) {
      displayTitle = (
        <div>
          {note.title.split(regex).map((part, index) => (
            <span key={index}>
              {part}
              {index === note.title.split(regex).length - 1 ? null : (
                <mark className="p-0">{searchQuery}</mark>
              )}
            </span>
          ))}
        </div>
      );
    }

    if (regex.test(note.content)) {
      // just the 70 characters around the first match
      const matchIndex = note.content.search(regex);
      const start = Math.max(0, matchIndex - 35);
      const end = Math.min(note.content.length, matchIndex + 35);
      displayContent = (
        <div>
          {start > 0 ? "..." : ""}
          {note.content
            .substring(start, end)
            .split(regex)
            .map((part, index) => (
              <span key={index}>
                {part}
                {index ===
                note.content.substring(start, end).split(regex).length -
                  1 ? null : (
                  <mark className="p-0">{searchQuery}</mark>
                )}
              </span>
            ))}
          {end < note.content.length ? "..." : ""}
        </div>
      );
    }
  }

  return (
    <LinkContainer
      to={`/note/${note.id}`}
      onClick={(e) => {
        openNoteById(note.id);
      }}
    >
      <div className="card note-card">
        <div className="card-body">
          <h5 className="card-title">{displayTitle}</h5>
          {showDelete && (
            <span className="position-absolute top-0 end-0">
              <NoteDeleteButton note={note} onDelete={onDelete} />
            </span>
          )}
          <span className="d-block mb-2">
            {note.tags.map((tag, index) => (
              <span
                key={index}
                className="badge me-1"
                style={{
                  backgroundColor: tag.color,
                  color: invertColor(tag.color),
                }}
              >
                {tag.name}
              </span>
            ))}
          </span>
          <div className="card-text">{displayContent}</div>
        </div>
      </div>
    </LinkContainer>
  );
}
