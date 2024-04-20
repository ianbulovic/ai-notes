from dataclasses import dataclass
from datetime import datetime
import re
from typing import Literal
import streamlit as st

from src.nlp import compare_embeddings, get_embedding, update_note_embedding
from src.note import Note, load_notes
from src.tag import Tag, load_tags


def search_controls() -> tuple[str, str, list[Tag] | None]:
    search_col, filter_col, sort_col = st.columns([2, 1, 1])
    with search_col:
        search_query = st.text_input(
            "Search by title, tag, or content", key="note-search"
        )
        search_query = search_query.strip()
    with filter_col:
        tags = load_tags()
        tag_filters = st.multiselect(
            "Filter by tags",
            options=tags,
            format_func=lambda t: t.name,
            key="tag-filters",
        )
        if not tag_filters:
            tag_filters = None
    with sort_col:
        sort_options = ["Last opened", "Creation date", "Title"]
        if search_query:
            sort_options.insert(0, "Relevance")
        sort_mode = st.selectbox("Sort by", sort_options)
        sort_mode = sort_mode or "Last opened"
    return search_query, sort_mode, tag_filters


@dataclass
class SearchResult:
    note: Note
    match_type: Literal["title", "tag", "content", "semantic"]
    match_text: str
    score: float = 0.0

    def as_card(self):
        note = self.note
        if note.tags:
            tag_spans = "".join([t.as_html_span() for t in note.tags])
        else:
            tag_spans = ""

        with st.container(border=True):
            with st.container(height=100, border=False):
                st.markdown(
                    f"<b style='white-space: nowrap; overflow: scroll; height: 40px;'>{note.title}</b>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='white-space: nowrap; overflow: scroll; height: auto; display: flex; gap: 10px; height: 30px;'>{tag_spans}</div>",
                    unsafe_allow_html=True,
                )
                if self.match_type == "content":
                    st.markdown(
                        f"<p style='white-space: nowrap; overflow: scroll; height: auto;'>{self.match_text}</p>",
                        unsafe_allow_html=True,
                    )
                elif self.match_type == "semantic":
                    st.markdown(
                        f"<p style='white-space: nowrap; overflow: scroll; height: auto;'>{self.match_text}</p>",
                        unsafe_allow_html=True,
                    )

            if st.button(
                "Open",
                key=note.title,
                use_container_width=True,
            ):
                st.session_state["current_note"] = note
                note.last_opened = datetime.now()
                note.save()
                st.switch_page("pages/note_page.py")


def get_search_results(
    notes: list[Note],
    search_query: str,
    sort_mode: str,
    tag_filters: list[Tag] | None,
    semantic_similarity_threshold: float = 0.55,
) -> list[SearchResult]:
    search_query_embedding = get_embedding(search_query)

    if tag_filters:
        notes = [note for note in notes if all(t in note.tags for t in tag_filters)]

    title_matches: list[SearchResult] = []
    tag_matches: list[SearchResult] = []
    content_matches: list[SearchResult] = []
    semantic_matches: list[SearchResult] = []
    for note in notes:
        if search_query.lower() in note.title.lower():
            title_matches.append(SearchResult(note, "title", note.title))
            continue
        matching_tags = [t for t in note.tags if search_query.lower() in t.name.lower()]
        if matching_tags:
            t = matching_tags[0]
            tag_matches.append(SearchResult(note, "tag", t.name))
            continue
        if search_query.lower() in note.content.lower():
            ctx_len = 10
            # regex to highlight the search query with ctx_len characters before and after
            rx = f"(.{{0,{ctx_len}}}){search_query}(.{{0,{ctx_len}}})"
            m = re.search(rx, note.content, re.IGNORECASE)
            if m:
                left_context, right_context = m.groups()
                left_context = left_context.replace("\n", " ")
                right_context = right_context.replace("\n", " ")
                match_text = f"...{left_context}<u>{search_query}</u>{right_context}..."
                content_matches.append(SearchResult(note, "content", match_text))
                continue
        cos_sim = compare_embeddings(search_query_embedding, note.embedding)
        if cos_sim > semantic_similarity_threshold:
            percent_sim = round(max(min((cos_sim + 0.5) * 80, 100), 0))
            semantic_matches.append(
                SearchResult(note, "semantic", f"{percent_sim}% match", cos_sim)
            )
            continue

    semantic_matches.sort(key=lambda result: result.score, reverse=True)
    results = title_matches + tag_matches + content_matches + semantic_matches
    if sort_mode == "Last opened":
        results.sort(key=lambda r: r.note.last_opened, reverse=True)
    elif sort_mode == "Creation date":
        results.sort(key=lambda r: r.note.created, reverse=True)
    elif sort_mode == "Title":
        results.sort(key=lambda r: r.note.title)

    return results


def note_search():
    with st.container():
        st.header("My Notes")

        notes = load_notes()
        if not notes:
            st.info(
                "You don't have any notes yet. Click the buttons above to create one."
            )
            st.stop()

        # create embeddings for notes that don't have them
        for note in notes:
            if not note.embedding:
                update_note_embedding(note)
                note.save()

        search_query, sort_mode, tag_filters = search_controls()
        results = get_search_results(notes, search_query, sort_mode, tag_filters)

        if search_query:
            st.write(
                f"Found {len(results)} {'note' if len(results) == 1 else 'notes'}."
            )
        n_cols = 4
        notes_columns = st.columns(n_cols)
        for i, result in enumerate(results):
            with notes_columns[i % n_cols]:
                result.as_card()
