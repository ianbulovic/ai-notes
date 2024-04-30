import React from "react";
import { Card } from "react-bootstrap";

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
      {content}
    </Card>
  );
}
