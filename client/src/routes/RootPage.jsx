import React, { useEffect, useState } from "react";
import { Pagination, Stack } from "react-bootstrap";

import Header from "../components/Header";
import SearchControls from "../components/SearchControls";
import NoteCard from "../components/NoteCard";

import { getNotes } from "../api";
import { APP_TITLE } from "../constants";

function PaginationControls(pageNumber, totalPages, setPageNumber) {
  return (
    <Pagination className="mx-auto mb-0" size="sm">
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

  const updateNotes = (query, sort, tags, resultsPerPage, pageNumber) => {
    getNotes(query, sort, tags, resultsPerPage, pageNumber).then(
      ({ notes, pages }) => {
        setNotes(notes);
        setTotalPages(pages);
      }
    );
  };

  useEffect(() => {
    updateNotes(searchQuery, sortBy, filterTags, resultsPerPage, pageNumber);
  }, [searchQuery, sortBy, filterTags, resultsPerPage, pageNumber]);

  useEffect(() => {
    document.title = APP_TITLE;
  });

  return (
    <div className="vh-100">
      <Header />
      {notes !== null ? (
        <>
          <SearchControls
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            setSortBy={setSortBy}
            filterTags={filterTags}
            setFilterTags={setFilterTags}
          />
          <Stack direction="vertical" gap={3} className="col-md-6 mx-auto px-4">
            {notes.length > 0 ? (
              <>
                {/* {PaginationControls(pageNumber, totalPages, setPageNumber)} */}
                {notes.map((note) => (
                  <NoteCard
                    key={note.id}
                    note={note}
                    onDelete={() =>
                      updateNotes(
                        searchQuery,
                        sortBy,
                        filterTags,
                        resultsPerPage,
                        pageNumber
                      )
                    }
                  />
                ))}
                {PaginationControls(pageNumber, totalPages, setPageNumber)}
                <div className="my-5" />
              </>
            ) : (
              <em className="h5 text-muted">No notes found.</em>
            )}
          </Stack>
        </>
      ) : (
        <Stack direction="vertical" gap={3} className="col-md-6 mx-auto px-4">
          <em className="h5 p-5 text-muted mx-auto">Connection error.</em>
        </Stack>
      )}
    </div>
  );
}
