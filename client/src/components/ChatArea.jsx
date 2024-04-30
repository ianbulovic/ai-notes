import React from "react";
import { useState } from "react";
import { Form, InputGroup, Button } from "react-bootstrap";
import SendIcon from "@mui/icons-material/Send";

import ChatCard from "./ChatCard";

import { chat } from "../api";
import { APP_TITLE } from "../constants";

export default function ChatArea({ note }) {
  const systemMessage = {
    role: "system",
    content: `You are a helpful AI assistant, integrated into a note-taking app called ${APP_TITLE}. 
    The user currently has open a note titled "${note.title}". Here is the note content:
    <NOTE CONTENT START>
    ${note.content}
    <NOTE CONTENT END>
    You can chat with the user to provide assistance or answer questions.`,
  };
  const aiIntroduction = {
    role: "assistant",
    content: `Hello! I'm your AI assistant. How can I help you today?`,
  };
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState([
    systemMessage,
    aiIntroduction,
  ]);
  const [thinking, setThinking] = useState(false);

  const handleSend = () => {
    chatHistory.push({ role: "user", content: chatInput });
    setThinking(true);
    setChatInput("");
    setChatHistory([...chatHistory]);
    chat(chatHistory).then((response) => {
      chatHistory.push(response);
      setChatHistory([...chatHistory]);
      setThinking(false);
    });
  };

  return (
    <div className="h-75">
      <ChatCard chatHistory={chatHistory} thinking={thinking} />
      <InputGroup className="mt-3">
        <Form.Control
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              handleSend();
            }
          }}
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          placeholder="Say something..."
          aria-label="Say something..."
        />
        <Button
          variant={chatInput ? "outline-primary" : "outline-secondary"}
          disabled={!chatInput}
          onClick={handleSend}
        >
          <SendIcon />
        </Button>
      </InputGroup>
    </div>
  );
}
