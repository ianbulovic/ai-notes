import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Card } from "react-bootstrap";

import "./ChatBubble.css";

export default function ChatBubble({ role, content }) {
  var style = {
    width: "fit-content",
    maxWidth: "75%",
    margin: "0.5rem",
    alignSelf: role === "user" ? "flex-end" : "flex-start",
  };
  if (role === "assistant") {
    style = {
      ...style,
      borderBottomLeftRadius: "0",
    };
  } else if (role === "user") {
    style = {
      ...style,
      borderBottomRightRadius: "0",
    };
  }
  return (
    <Card
      bg={role === "user" ? "primary" : "secondary"}
      text="white"
      className="px-2 py-1"
      style={style}
    >
      {role === "user" ? (
        content
      ) : (
        <ReactMarkdown
          className="p-0 m-0 markdown-container"
          remarkPlugins={[remarkGfm]}
          components={{
            h1: "h2",
            h2: "h3",
            h3: "h4",
            h4: "h5",
          }}
        >
          {content}
        </ReactMarkdown>
      )}
    </Card>
  );
}
