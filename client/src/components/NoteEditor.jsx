import React, { useState, useRef, useEffect } from "react";
import { Form, Stack } from "react-bootstrap";

import { updateNote, updateNoteEmbedding } from "../api";

export default function NoteEditor({ note, setNote }) {
  const titleRef = useRef();
  const textareaRef = useRef();

  const [title, setTitle] = useState(note.title);
  const [content, setContent] = useState(note.content);
  const [dirty, setDirty] = useState(false);
  const [lastSaved, setLastSaved] = useState(Date.now());
  const [embeddingDirty, setEmbeddingDirty] = useState(false);
  const [lastEmbeddingSaved, setLastEmbeddingSaved] = useState(Date.now());

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

  const handleTitleChange = (e) => {
    setTitle(e.target.value);
    setDirty(true);
    setEmbeddingDirty(true);
  };

  const handleContentChange = (e) => {
    setContent(e.target.value);
    resizeTextarea();
    setDirty(true);
    setEmbeddingDirty(true);
  };

  useEffect(() => {
    if (!dirty) return;

    const save = (now) => {
      setLastSaved(now);
      updateNote(note.id, { title, content }).then((responseNote) => {
        setNote(responseNote);
        if (responseNote.title === title && responseNote.content === content) {
          setDirty(false);
        }
      });
    };

    const now = Date.now();
    if (now - lastSaved > 1000) {
      save(now);
    } else {
      const timeout = setTimeout(() => {
        save(Date.now());
      }, 1000);
      return () => clearTimeout(timeout);
    }
  }, [content, dirty, lastSaved, note.id, setNote, title]);

  // useEffect(() => {
  //   if (!embeddingDirty) return;

  //   const saveEmbedding = (now) => {
  //     setLastEmbeddingSaved(now);
  //     updateNoteEmbedding(note.id).then((responseNote) => {
  //       setNote(responseNote);
  //       if (responseNote.content === content) {
  //         setEmbeddingDirty(false);
  //       }
  //     });
  //   };

  //   const now = Date.now();

  //   if (now - lastEmbeddingSaved > 5000) {
  //     saveEmbedding(now);
  //   } else {
  //     const timeout = setTimeout(() => {
  //       saveEmbedding(Date.now());
  //     }, 5000);
  //     return () => clearTimeout(timeout);
  //   }
  // }, [content, embeddingDirty, lastEmbeddingSaved, note.id, setNote]);

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
