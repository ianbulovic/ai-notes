import React, { useEffect, useState } from "react";
import { Stack, Badge, Dropdown, CloseButton } from "react-bootstrap";
import AddIcon from "@mui/icons-material/Add";
import NewTagModal from "./NewTagModal";

import { addTagToNote, removeTagFromNote, getTags, getNoteById } from "../api";
import { invertColor } from "../utils";

export default function NoteTagList({ note, setNote }) {
  const [allTags, setAllTags] = useState([]);
  const [showNewTagModal, setShowNewTagModal] = useState(false);

  const refreshTags = () => {
    getTags().then(({ tags }) => setAllTags(tags));
  };

  const refreshNote = () => {
    getNoteById(note.id).then((responseNote) => {
      setNote(responseNote);
    });
  };

  useEffect(refreshTags, []);

  return (
    <Stack
      direction="horizontal"
      gap={2}
      className="d-flex flex-wrap align-items-center"
    >
      <NewTagModal
        note={note}
        show={showNewTagModal}
        setShow={setShowNewTagModal}
        refresh={() => {
          refreshTags();
          refreshNote();
        }}
      />
      <Dropdown>
        <h5>
          <Dropdown.Toggle as={Badge} className="bg-secondary">
            Add a tag
          </Dropdown.Toggle>
        </h5>
        <Dropdown.Menu>
          <Dropdown.Item
            className="h5"
            onClick={() => setShowNewTagModal(true)}
          >
            <span className="badge bg-secondary">
              New tag
              <AddIcon fontSize="inherit" className="ms-1" />
            </span>
          </Dropdown.Item>
          {allTags.map((tag) => (
            <Dropdown.Item
              key={tag.id}
              className="h5"
              onClick={() => {
                addTagToNote(note.id, tag.id).then((responseNote) => {
                  setNote(responseNote);
                });
              }}
            >
              <span
                key={tag}
                className="badge"
                style={{
                  backgroundColor: tag.color,
                  color: invertColor(tag.color),
                  textAlign: "left",
                }}
              >
                {tag.name}
              </span>
            </Dropdown.Item>
          ))}
        </Dropdown.Menu>
      </Dropdown>
      {note.tags?.map((tag, index) => (
        <h5 key={index}>
          <div
            className="badge me-1"
            style={{
              backgroundColor: tag.color,
              color: invertColor(tag.color),
              // vertically align the text
              display: "inline-flex",
              alignItems: "center",
            }}
          >
            {tag.name}
            <CloseButton
              className="ms-1"
              style={{
                fontSize: "7pt",
                opacity: 1,
                filter:
                  (invertColor(tag.color) === "#000000" && "invert(0)") ||
                  "invert(1)",
              }}
              onClick={() => {
                removeTagFromNote(note.id, tag.id).then((responseNote) => {
                  setNote(responseNote);
                });
              }}
            />
          </div>
        </h5>
      ))}
    </Stack>
  );
}
