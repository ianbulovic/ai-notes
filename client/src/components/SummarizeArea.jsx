import React, { useState } from "react";
import { Button, Spinner, Stack } from "react-bootstrap";

import { summarize } from "../api";

export default function SummarizeArea({ note }) {
  const [summary, setSummary] = useState("");
  const [thinking, setThinking] = useState(false);

  const generateSummary = () => {
    setThinking(true);
    summarize(note.content).then(({ summary }) => {
      setSummary(summary);
      setThinking(false);
    });
  };

  return (
    <Stack
      direction="vertical"
      gap={3}
      style={{
        height: "calc(100vh - 250px)",
      }}
    >
      <Button
        variant="primary"
        style={{ margin: "10px" }}
        onClick={generateSummary}
      >
        Generate Summary
      </Button>
      {thinking && (
        <Spinner animation="border" role="status" style={{ margin: "10px" }} />
      )}
      {summary.length > 0 && (
        <div
          style={{
            margin: "10px",
            padding: "10px",
            border: "1px solid #ccc",
            borderRadius: "5px",
          }}
        >
          {summary}
        </div>
      )}
    </Stack>
  );
}
