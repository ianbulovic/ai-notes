import React from "react";
import { Card, Spinner, Stack } from "react-bootstrap";
import ChatBubble from "./ChatBubble";

export default function ChatCard({ chatHistory, thinking }) {
  return (
    <Card style={{ height: "75%" }}>
      <Card.Body style={{ height: "100%" }}>
        <Card.Title>Chat with AI about your note</Card.Title>
        <Stack
          style={{
            height: "calc(100% - 2.5rem)",
            overflow: "scroll",
            display: "flex",
            flexDirection: "column-reverse",
          }}
        >
          <div>
            {thinking && <Spinner animation="border" variant="secondary" />}
          </div>
          {chatHistory
            .toReversed()
            .map(
              (message, index) =>
                (message.role === "assistant" || message.role === "user") && (
                  <ChatBubble
                    key={index}
                    role={message.role}
                    content={message.content}
                  />
                )
            )}
        </Stack>
      </Card.Body>
    </Card>
  );
}
