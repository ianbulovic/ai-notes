import React, { useState, useEffect } from "react";
import { Stack, Card, Form, Row, Col, InputGroup } from "react-bootstrap";

import TagDeleteButton from "./TagDeleteButton";

import { getTags, getTagById, updateTag } from "../api";
import { invertColor } from "../utils";

function TagCard({ tagId, initialTag, onDelete }) {
  const [tag, setTag] = useState(initialTag);
  const [name, setName] = useState(tag.name);
  const [color, setColor] = useState(tag.color);

  useEffect(() => {
    getTagById(tagId).then((tag) => setTag(tag));
  }, [tagId, setTag, setName, setColor]);

  const updateTagData = (newName, newColor) => {
    newName = newName || "New tag";
    updateTag(tagId, { name: newName, color: newColor }).then((t) => {
      setTag(t);
      setName(t.name);
      setColor(t.color);
    });
  };

  return (
    <Card>
      <Card.Body>
        <div
          className="badge mx-auto p-2 mb-3"
          style={{
            cursor: "pointer",
            color: invertColor(tag.color),
            backgroundColor: tag.color,
            fontSize: "1rem",
          }}
        >
          {tag.name}
        </div>
        <div className="position-absolute top-0 end-0">
          <TagDeleteButton tag={tag} onDelete={onDelete} />
        </div>
        <Row>
          <Col>
            <InputGroup>
              <Form.Control
                type="text"
                placeholder="Tag name"
                onChange={(e) => {
                  setName(e.target.value);
                  updateTagData(e.target.value, color);
                }}
                value={name}
              />
            </InputGroup>
          </Col>
          <Col xs="auto">
            <InputGroup>
              <InputGroup.Text>Tag color</InputGroup.Text>
              <Form.Control
                type="color"
                title="Tag color"
                style={{
                  width: "3rem",
                }}
                value={color}
                onChange={(e) => {
                  setColor(e.target.value);
                  updateTagData(name, e.target.value);
                }}
              />
            </InputGroup>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );
}

export default function TagManager() {
  const [tags, setTags] = useState([]);

  const refreshTags = () => {
    getTags().then(({ tags }) => setTags(tags));
  };

  useEffect(refreshTags, []);

  return (
    <div>
      <h2>Manage Tags</h2>
      <Stack gap={4} className="mt-4">
        {tags.map((tag) => (
          <TagCard
            key={tag.id}
            tagId={tag.id}
            onDelete={refreshTags}
            initialTag={tag}
          />
        ))}
      </Stack>
    </div>
  );
}
