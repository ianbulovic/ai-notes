import React, { useState, useEffect } from "react";
import { useAudioRecorder } from "react-audio-voice-recorder";
import { Stack, InputGroup, Button, Spinner } from "react-bootstrap";

import Header from "../components/Header";

import {
  uploadRecording,
  createNote,
  addMediaToNote,
  transcribeRecording,
  updateNote,
} from "../api";

export default function RecordingPage() {
  const {
    startRecording,
    stopRecording,
    togglePauseResume,
    recordingBlob,
    isRecording,
    isPaused,
    // recordingTime,
    // mediaRecorder,
  } = useAudioRecorder();

  const [url, setUrl] = useState(null);
  const [processing, setProcessing] = useState(false);

  const saveRecording = () => {
    if (!recordingBlob) return;
    setProcessing(true);
    uploadRecording(recordingBlob).then(({ id: mediaId }) => {
      createNote().then((note) => {
        addMediaToNote(note.id, mediaId).then((noteWithMedia) => {
          transcribeRecording(mediaId).then(({ text }) => {
            updateNote(note.id, { content: text }).then(() => {
              window.location.href = `/note/${note.id}`;
            });
          });
        });
      });
    });
  };

  useEffect(() => {
    if (!recordingBlob) return;

    setUrl(URL.createObjectURL(recordingBlob));
  }, [recordingBlob]);

  return (
    <div className="vh-100">
      <Header />
      <Stack direction="vertical" gap={3} className="col-md-4 mx-auto p-4 ">
        <h1 className="mx-auto mb-5">Record a Voice Note</h1>
        {!isRecording ? (
          url ? (
            <Button
              onClick={() => setUrl(null)}
              variant="danger"
              style={{ fontSize: "1.5rem" }}
            >
              Clear Recording
            </Button>
          ) : (
            <Button
              onClick={startRecording}
              disabled={isRecording}
              variant="primary"
              style={{ fontSize: "1.5rem" }}
            >
              Start Recording
            </Button>
          )
        ) : (
          <InputGroup className="w-100">
            <Button
              onClick={stopRecording}
              disabled={!isRecording}
              variant="danger"
              className="w-50"
              style={{ fontSize: "1.5rem" }}
            >
              Stop Recording
            </Button>
            <Button
              onClick={togglePauseResume}
              disabled={!isRecording}
              variant="warning"
              className="w-50"
              style={{ fontSize: "1.5rem" }}
            >
              {isPaused ? "Resume" : "Pause"}
            </Button>
          </InputGroup>
        )}

        {url && (
          <audio
            controls
            src={url}
            className="bg-info rounded-3"
            style={{
              width: "100%",
              display: "block",
            }}
          />
        )}
        {url && (
          <Button
            onClick={saveRecording}
            variant="success"
            style={{ fontSize: "1.5rem" }}
          >
            Transcribe and Create Note
          </Button>
        )}
        {processing && <Spinner animation="border" className="mx-auto" />}
      </Stack>
    </div>
  );
}
