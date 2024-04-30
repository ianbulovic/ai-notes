import React from "react";
import { useState } from "react";
import { Modal, Button, Form, InputGroup, Row, Col } from "react-bootstrap";

import { createTag, addTagToNote } from "../api";
import { invertColor } from "../utils";

export default function NewTagModal({ note, show, setShow, refresh }) {
  const [name, setName] = useState("");
  const [color, setColor] = useState("#AF3FAF");

  const closeModal = () => {
    setShow(false);
  };

  const submitTag = (name, color) => {
    createTag({ name, color }).then((newTag) => {
      addTagToNote(note.id, newTag.id).then(() => {
        closeModal();
        refresh();
      });
    });
  };

  return (
    <Modal show={show} onHide={() => setShow(false)}>
      <Form>
        <Modal.Header closeButton>
          <Modal.Title>New Tag</Modal.Title>
        </Modal.Header>
        <Modal.Body
          style={{
            height: "5.5rem",
          }}
        >
          <Row>
            <Col>
              <InputGroup hasValidation>
                <Form.Control
                  type="text"
                  placeholder="Tag name"
                  required
                  isInvalid={!name}
                  onChange={(e) => setName(e.target.value)}
                  autoFocus
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a tag name.
                </Form.Control.Feedback>
              </InputGroup>
            </Col>
            <Col xs="auto">
              <InputGroup>
                <InputGroup.Text>Tag color</InputGroup.Text>
                <Form.Control
                  type="color"
                  title="Tag color"
                  style={{
                    width: "3rem",
                  }}
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                />
              </InputGroup>
            </Col>
          </Row>
        </Modal.Body>
        <Modal.Footer>
          <span className="me-auto">
            <span
              className="badge"
              style={{
                backgroundColor: color,
                color: invertColor(color),
                marginLeft: "0.5rem",
                fontSize: "1rem",
              }}
            >
              {name || "New tag"}
            </span>
          </span>
          <Button variant="secondary" onClick={closeModal}>
            Cancel
          </Button>
          <Button onClick={() => submitTag(name, color)} disabled={!name}>
            Create
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}
