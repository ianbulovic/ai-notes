import React, { useEffect, useState, useRef } from "react";
import {
  InputGroup,
  Form,
  FloatingLabel,
  Dropdown,
  CloseButton,
  Stack,
} from "react-bootstrap";

import { invertColor } from "../utils";

import { getTags } from "../api";

export default function SearchControls({
  searchQuery,
  setSearchQuery,
  setSortBy,
  filterTags,
  setFilterTags,
}) {
  const [searchTags, setSearchTags] = useState([]);
  const [tagSearchQuery, setTagSearchQuery] = useState("");

  const sortRef = useRef();

  useEffect(() => {
    getTags().then(({ tags }) => {
      setSearchTags(tags);
    });
  }, []);

  return (
    <div className="col-md-6 mx-auto p-4">
      <InputGroup className="mb-3 w-100">
        <FloatingLabel
          controlId="search"
          label="Search notes by title or content"
        >
          <Form.Control
            aria-label="Search notes"
            onChange={(e) => {
              if (!searchQuery && e.target.value) {
                setSortBy("relevance");
                sortRef.current.value = "relevance";
              }
              setSearchQuery(e.target.value);
            }}
            type="search"
            placeholder="Search by note title or content"
            value={searchQuery}
          />
        </FloatingLabel>
        <FloatingLabel
          controlId="sortBy"
          label="Sort by"
          style={{ maxWidth: "30%" }}
        >
          <Form.Select
            aria-label="Sort mode"
            onChange={(e) => setSortBy(e.target.value)}
            ref={sortRef}
          >
            {searchQuery && <option value="relevance">Relevance</option>}
            <option value="opened">Last Opened</option>
            <option value="modified">Last Modified</option>
            <option value="created">Creation Date</option>
            <option value="title">Title</option>
          </Form.Select>
        </FloatingLabel>
      </InputGroup>
      <Stack direction="horizontal" className="gap-3">
        <Dropdown onToggle={() => setTagSearchQuery("")}>
          <Dropdown.Toggle variant="outline-secondary">
            Filter by tag
          </Dropdown.Toggle>
          <Dropdown.Menu>
            <Form.Control
              autoFocus
              className="mx-3 my-2 w-auto"
              placeholder="Search tags..."
              onChange={(e) => setTagSearchQuery(e.target.value)}
              value={tagSearchQuery}
            />
            {searchTags
              .sort((a, b) => a.name.toLowerCase() > b.name.toLowerCase())
              .map(
                (tag) =>
                  tag.name
                    .toLowerCase()
                    .includes(tagSearchQuery.toLowerCase()) && (
                    <Dropdown.Item
                      key={tag.id}
                      className="h5"
                      onClick={() => {
                        setFilterTags([...filterTags, tag]);
                        setTagSearchQuery("");
                        setSearchTags(searchTags.filter((t) => t !== tag));
                      }}
                    >
                      <span
                        key={tag}
                        className="badge"
                        style={{
                          backgroundColor: tag.color,
                          color: invertColor(tag.color),
                          textAlign: "left",
                        }}
                      >
                        {tag.name}
                      </span>
                    </Dropdown.Item>
                  )
              )}
          </Dropdown.Menu>
        </Dropdown>
        {filterTags.map((tag) => (
          <div key={tag} className="h4 my-auto">
            <div
              className="badge"
              style={{
                backgroundColor: tag.color,
                color: invertColor(tag.color),
                display: "inline-flex",
                alignItems: "center",
              }}
            >
              {tag.name}
              <CloseButton
                className="ms-1"
                style={{
                  fontSize: "7pt",
                  opacity: 1,
                  filter:
                    (invertColor(tag.color) === "#000000" && "invert(0)") ||
                    "invert(1)",
                }}
                onClick={() => {
                  setFilterTags(filterTags.filter((t) => t !== tag));
                  setSearchTags([...searchTags, tag]);
                }}
              />
            </div>
          </div>
        ))}
      </Stack>
    </div>
  );
}
