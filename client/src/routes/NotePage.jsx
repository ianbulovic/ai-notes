import React from "react";
import { useEffect } from "react";
import { Stack, Tab, Nav, Row, Col } from "react-bootstrap";
import { useLoaderData } from "react-router-dom";

import Header from "../components/Header";
import NoteEditor from "../components/NoteEditor";
import NotePreview from "../components/NotePreview";
import NoteTagList from "../components/NoteTagList";

import { getNoteById, getMediaById } from "../api";
import { APP_TITLE } from "../constants";
import ChatArea from "../components/ChatArea";

export async function loader({ params }) {
  const noteOnLoad = await getNoteById(params.id);
  return { noteOnLoad };
}

const NotePage = () => {
  const { noteOnLoad } = useLoaderData();
  const [note, setNote] = React.useState(noteOnLoad);
  const [audio, setAudio] = React.useState(null);

  useEffect(() => {
    if (note.media && note.media.length > 0) {
      const mediaId = note.media[0];
      getMediaById(mediaId).then((blob) => {
        const url = URL.createObjectURL(blob);
        setAudio({ url });
      });
    }
  }, [note.media]);

  useEffect(() => {
    document.title = `${note.title || "Untitled Note"} - ${APP_TITLE}`;
  }, [note.title]);

  return (
    <div>
      <Header />
      <Stack
        direction="vertical"
        gap={3}
        className="col-md-6 mx-auto p-4"
        style={{
          minHeight: "80vh",
        }}
      >
        <NoteTagList note={note} setNote={setNote} />
        {audio && (
          <Stack gap={1}>
            <em className="text-muted">Recorded audio:</em>
            <audio
              controls
              src={audio.url}
              className="bg-info rounded-3"
              style={{
                width: "100%",
                display: "block",
              }}
            />
          </Stack>
        )}
        <Tab.Container defaultActiveKey="edit">
          <Nav variant="tabs">
            <Nav.Item>
              <Nav.Link eventKey="edit" variant="secondary">
                Edit
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="view" variant="secondary">
                View
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="chat" variant="secondary">
                Chat
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="summarize" variant="secondary">
                Summarize
              </Nav.Link>
            </Nav.Item>
          </Nav>
          <Tab.Content>
            <Tab.Pane eventKey="edit">
              <NoteEditor note={note} setNote={setNote} />
            </Tab.Pane>
            <Tab.Pane eventKey="view">
              <NotePreview note={note} />
            </Tab.Pane>
            <Tab.Pane eventKey="chat">
              <Row
                gap={3}
                style={{
                  position: "relative",
                  right: "30%",
                  width: "160%",
                  minHeight: "100%",
                }}
              >
                <Col>
                  <NotePreview note={note} />
                </Col>
                <Col>
                  <ChatArea note={note} />
                </Col>
              </Row>
            </Tab.Pane>
            <Tab.Pane eventKey="summarize">
              <Row
                gap={3}
                style={{
                  position: "relative",
                  right: "30%",
                  width: "160%",
                  minHeight: "100%",
                }}
              >
                <Col>
                  <NotePreview note={note} />
                </Col>
                <Col>
                  <em className="text-muted">Not yet implemented.</em>
                </Col>
              </Row>
            </Tab.Pane>
          </Tab.Content>
        </Tab.Container>
        <div className="pt-5" /> {/* Spacer */}
      </Stack>
    </div>
  );
};

export default NotePage;
