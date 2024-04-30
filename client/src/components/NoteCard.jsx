import { LinkContainer } from "react-router-bootstrap";
import "./NoteCard.css";
import { openNoteById } from "../api";
import { invertColor } from "../utils";
import NoteDeleteButton from "./NoteDeleteButton";

export default function NoteCard({ note, onDelete }) {
  return (
    <LinkContainer
      to={`/note/${note.id}`}
      onClick={(e) => {
        openNoteById(note.id);
      }}
    >
      <div className="card note-card">
        <div className="card-body">
          <h5 className="card-title">{note.title}</h5>
          <span className="position-absolute top-0 end-0">
            <NoteDeleteButton note={note} onDelete={onDelete} />
          </span>
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
          <p className="card-text">
            {note.content.substring(0, 70) +
              (note.content.length > 70 ? "..." : "")}
          </p>
        </div>
      </div>
    </LinkContainer>
  );
}
