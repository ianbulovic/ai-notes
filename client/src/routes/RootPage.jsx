import React, { useEffect, useState, useRef } from "react";
import { Pagination, Stack, Tab, Nav } from "react-bootstrap";
import { debounce } from "lodash";

import Header from "../components/Header";
import SearchControls from "../components/SearchControls";
import NoteCard from "../components/NoteCard";

import { getNotes } from "../api";
import { APP_TITLE } from "../constants";
import RagArea from "../components/RagArea";

function PaginationControls(pageNumber, totalPages, setPageNumber) {
  return (
    <Pagination className="mx-auto mb-0 mt-3" size="sm">
      <Pagination.Prev
        onClick={() => {
          window.scrollTo({ top: 0 });
          setPageNumber(pageNumber - 1);
        }}
        disabled={pageNumber === 1}
      />
      {Array.from({ length: totalPages }, (_, i) => (
        <Pagination.Item
          key={i}
          active={i + 1 === pageNumber}
          onClick={() => {
            window.scrollTo({ top: 0 });
            setPageNumber(i + 1);
          }}
        >
          {i + 1}
        </Pagination.Item>
      ))}
      <Pagination.Next
        onClick={() => {
          window.scrollTo({ top: 0 });
          setPageNumber(pageNumber + 1);
        }}
        disabled={pageNumber === totalPages}
      />
    </Pagination>
  );
}

export default function RootPage() {
  const [notes, setNotes] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("opened");
  const [filterTags, setFilterTags] = useState([]);

  const [resultsPerPage, setResultsPerPage] = useState(20);
  const [pageNumber, setPageNumber] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const updateNotes = ({
    searchQuery,
    sortBy,
    filterTags,
    resultsPerPage,
    pageNumber,
  }) => {
    getNotes(searchQuery, sortBy, filterTags, resultsPerPage, pageNumber).then(
      ({ notes, pages }) => {
        setNotes(notes);
        setTotalPages(pages);
      }
    );
  };

  const debouncedUpdateNotes = useRef(
    debounce((params) => updateNotes(params), 200, {
      trailing: true,
    })
  ).current;

  useEffect(() => {
    debouncedUpdateNotes({
      searchQuery,
      sortBy,
      filterTags,
      resultsPerPage,
      pageNumber,
    });

    return () => {
      debouncedUpdateNotes.cancel();
    };
  }, [
    searchQuery,
    sortBy,
    filterTags,
    resultsPerPage,
    pageNumber,
    debouncedUpdateNotes,
  ]);

  useEffect(() => {
    document.title = APP_TITLE;
  });

  return (
    <div className="vh-100">
      <Header />
      {notes !== null ? (
        <Stack direction="vertical" gap={3} className="col-md-6 mx-auto p-4">
          <Tab.Container defaultActiveKey="search">
            <Nav fill justify variant="tabs">
              <Nav.Item>
                <Nav.Link eventKey="search" variant="secondary">
                  Search Notes
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="rag" variant="secondary">
                  Ask a Question
                </Nav.Link>
              </Nav.Item>
            </Nav>
            <Tab.Content>
              <Tab.Pane eventKey="search">
                <SearchControls
                  searchQuery={searchQuery}
                  setSearchQuery={setSearchQuery}
                  setSortBy={setSortBy}
                  filterTags={filterTags}
                  setFilterTags={setFilterTags}
                />
                {notes.length > 0 ? (
                  <Stack gap={2}>
                    {/* {PaginationControls(pageNumber, totalPages, setPageNumber)} */}
                    {notes.map((note) => (
                      <NoteCard
                        key={note.id}
                        note={note}
                        searchQuery={searchQuery}
                        onDelete={() =>
                          updateNotes(
                            searchQuery,
                            sortBy,
                            filterTags,
                            resultsPerPage,
                            pageNumber
                          )
                        }
                        showDelete={true}
                      />
                    ))}
                    {PaginationControls(pageNumber, totalPages, setPageNumber)}
                    <div className="my-5" />
                  </Stack>
                ) : (
                  <em className="h5 text-muted">No notes found.</em>
                )}
              </Tab.Pane>
              <Tab.Pane eventKey="rag">
                <RagArea />
              </Tab.Pane>
            </Tab.Content>
          </Tab.Container>
        </Stack>
      ) : (
        <Stack direction="vertical" gap={3} className="col-md-6 mx-auto px-4">
          <em className="h5 p-5 text-muted mx-auto">Connection error.</em>
        </Stack>
      )}
    </div>
  );
}
