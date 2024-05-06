import React, { useState, useRef, useEffect } from "react";
import { Form, Stack } from "react-bootstrap";
import { debounce } from "lodash";

import { updateNote, updateNoteEmbedding } from "../api";

export default function NoteEditor({ note, setNote }) {
  const titleRef = useRef();
  const textareaRef = useRef();

  const [title, setTitle] = useState(note.title);
  const [content, setContent] = useState(note.content);
  const [dirty, setDirty] = useState(false);

  const resizeTextarea = () => {
    const textarea = textareaRef.current;

    // use a clone to measure the height of the textarea
    // this prevents the window from scrolling to the top when the textarea is resized
    const clone = textarea.cloneNode();
    clone.style.width = `${textarea.offsetWidth}px`;
    clone.style.height = "auto";
    clone.style.position = "absolute";
    document.body.appendChild(clone);
    const height = clone.scrollHeight;

    // set the height of the textarea
    textarea.style.height = `${Math.max(height, 300)}px`;

    clone.remove();
  };
  useEffect(resizeTextarea, []);

  const sendUpdate = ({ newTitle, newContent }) => {
    updateNote(note.id, { title: newTitle, content: newContent }).then(
      (responseNote) => {
        setNote(responseNote);
      }
    );
  };

  const debouncedSendUpdate = useRef(
    debounce(sendUpdate, 1000, { leading: true, trailing: true })
  ).current;

  useEffect(() => {
    if (title !== note.title || content !== note.content) {
      setDirty(true);
      debouncedSendUpdate({ newTitle: title, newContent: content });
    } else {
      setDirty(false);
    }
  }, [title, content, note.title, note.content, debouncedSendUpdate]);

  const handleTitleChange = (e) => {
    setTitle(e.target.value);
  };

  const handleContentChange = (e) => {
    setContent(e.target.value);
    resizeTextarea();
  };

  useEffect(() => {
    return () => updateNoteEmbedding(note.id);
  }, [note.id]);

  window.addEventListener("beforeunload", () => {
    updateNoteEmbedding(note.id);
  });

  return (
    <Stack direction="vertical" gap={3} className="mx-auto pb-5">
      <small className="text-muted">
        <em>{dirty ? "Saving..." : "Changes saved."}</em>
      </small>

      <Form.Control
        ref={titleRef}
        size="lg"
        type="text"
        value={title}
        onChange={handleTitleChange}
      />
      <Form.Control
        as="textarea"
        ref={textareaRef}
        type="text"
        value={content}
        style={{
          minHeight: "50%",
          lineHeight: "1.5",
          overflowY: "hidden",
        }}
        onChange={handleContentChange}
      />
    </Stack>
  );
}
