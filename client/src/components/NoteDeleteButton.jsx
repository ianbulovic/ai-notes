import React, { useState } from "react";
import { Modal } from "react-bootstrap";
import DeleteIcon from "@mui/icons-material/Delete";

import { deleteNote } from "../api";

export default function NoteDeleteButton({ note, onDelete }) {
  const [showModal, setShowModal] = useState(false);
  const [hover, setHover] = useState(false);

  const handleDelete = () => {
    deleteNote(note.id).then(() => {
      onDelete();
    });
  };

  return (
    <div
      className="p-1 m-1"
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onClick={(e) => {
        setShowModal(true);
        setHover(false);
        e.preventDefault();
        e.stopPropagation();
      }}
      style={{
        cursor: "pointer",
      }}
    >
      <DeleteIcon className={`${hover ? "text-danger" : "text-muted"}`} />
      <div onClick={(e) => e.stopPropagation()}>
        <Modal show={showModal} onHide={() => setShowModal(false)}>
          <Modal.Header closeButton>
            <Modal.Title>Delete note</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            Are you sure you want to delete "{note.title}"?
          </Modal.Body>
          <Modal.Footer>
            <button
              className="btn btn-secondary"
              onClick={() => setShowModal(false)}
            >
              Cancel
            </button>
            <button
              className="btn btn-danger"
              onClick={() => {
                handleDelete();
                setShowModal(false);
              }}
            >
              Delete
            </button>
          </Modal.Footer>
        </Modal>
      </div>
    </div>
  );
}
