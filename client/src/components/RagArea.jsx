import React from "react";
import { useState } from "react";
import {
  Stack,
  Form,
  InputGroup,
  Button,
  Spinner,
  Card,
} from "react-bootstrap";
import SendIcon from "@mui/icons-material/Send";

import { chat, getNotesByQuery } from "../api";
import { APP_TITLE } from "../constants";
import NoteCard from "./NoteCard";

const generateSystemMessage = (notes) => {
  return {
    role: "system",
    content: `You are a helpful AI assistant, integrated into a note-taking app called ${APP_TITLE}.
        Your job is to answer questions based on the content of the user's notes.
        The following is a list of notes that the system has retrieved as possibly relevant to the user's query. This system is not perfect, so if the notes are not relevant, please let the user know that you are unable to assist by saying "I'm sorry, I am unable to assist with that." If you are able to answer the user's question, please provide the answer and make sure to include the title of the note (or notes) that the answer is based on.
        Here are the notes that the system has retrieved:
        ${JSON.stringify(notes, ["title", "content"], 2)}`,
  };
};

export default function RagArea({ note }) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("");
  const [response, setResponse] = useState("");
  const [references, setReferences] = useState([]);

  const handleSend = () => {
    setStatus("Searching for notes...");
    setResponse("");
    setReferences([]);
    getNotesByQuery(query, 5).then(({ notes }) => {
      setStatus("Searching notes for information...");
      if (notes.length === 0) {
        setQuery("");
        setStatus("");
        setResponse({
          role: "assistant",
          content: "I couldn't find any notes that might help with that.",
        });
        return;
      }
      setReferences(notes);
      const systemMessage = generateSystemMessage(notes);
      const messages = [
        systemMessage,
        {
          role: "user",
          content: query,
        },
      ];
      chat(messages).then((response) => {
        setQuery("");
        setStatus("");
        setResponse(response);
      });
    });
  };

  return (
    <Stack>
      <InputGroup>
        <Form.Control
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              handleSend();
            }
          }}
          disabled={status.length > 0}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question..."
          aria-label="Ask a question..."
        />
        <Button
          variant={
            query && status.length === 0
              ? "outline-primary"
              : "outline-secondary"
          }
          disabled={!query || status.length > 0}
          onClick={handleSend}
        >
          <SendIcon />
        </Button>
      </InputGroup>
      {status.length > 0 && (
        <Stack direction="horizontal" gap={3} className="mx-auto py-3">
          <Spinner animation="border" variant="secondary" />
          {status}
        </Stack>
      )}
      {response && (
        <Card className="my-5 p-2 bg-secondary">{response.content}</Card>
      )}
      {references.length > 0 && (
        <Stack gap={3}>
          {references.map((note) => (
            <NoteCard
              key={note.id}
              note={note}
              searchQuery=""
              onDelete={() => {}}
            />
          ))}
        </Stack>
      )}
    </Stack>
  );
}
