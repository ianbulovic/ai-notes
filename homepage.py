from datetime import datetime
import streamlit as st
from src.note import Note, load_notes
from src.tag import load_tags, delete_tag

if "current_note" in st.session_state:
    del st.session_state["current_note"]

st.set_page_config(page_title="My Notes - AI Notes", page_icon="📝")

st.markdown(
    "<h1 style='text-align: center'>AI Notes</h1>",
    unsafe_allow_html=True,
)

l, r = st.columns(2)
with l:
    if st.button("New Note :memo:", type="primary", use_container_width=True):
        note = Note()
        st.session_state["current_note"] = note
        st.switch_page("pages/note_page.py")
with r:
    if st.button(
        "New Voice Note :studio_microphone:", type="primary", use_container_width=True
    ):
        note = Note()
        st.session_state["current_note"] = note
        st.switch_page("pages/record_voicenote.py")

view_notes_tab, manage_tags_tab = st.tabs(["View Notes", "Manage Tags"])

with view_notes_tab:
    st.header("My Notes")

    l, r = st.columns([3, 1])
    with l:
        search_query = st.text_input("Search by title or tag", key="note-search")
    with r:
        sort_mode = st.selectbox("Sort by", ["Last opened", "Creation date", "Title"])
        sort_mode = sort_mode or "Last opened"

    notes = load_notes(search_query, sort_mode)
    if not notes:
        st.info("You don't have any notes yet. Click the buttons above to create one.")
        st.stop()

    notes_columns = st.columns(3)
    for i, note in enumerate(notes):
        with notes_columns[i % 3]:
            if note.tags:
                tag_spans = "".join([t.as_html_span() for t in note.tags])
            else:
                tag_spans = ""

            with st.container(border=True):
                with st.container(height=100, border=False):
                    st.markdown(
                        f"<b style='white-space: nowrap; overflow: scroll; height: 50px;'>{note.title}</b>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='white-space: nowrap; overflow: scroll; height: auto; display: flex; gap: 10px'>{tag_spans}</div>",
                        unsafe_allow_html=True,
                    )
                    # st.markdown(tag_spans, unsafe_allow_html=True)
                if st.button(
                    "Open",
                    key=note.title,
                    use_container_width=True,
                ):
                    st.session_state["current_note"] = note
                    note.last_opened = datetime.now()
                    note.save()
                    st.switch_page("pages/note_page.py")

with manage_tags_tab:
    st.header("Manage Tags")
    search_query = st.text_input("Search tags", key="tag-search")
    results = load_tags()
    if search_query:
        results = [tag for tag in results if search_query.lower() in tag.name.lower()]
    tag_cols = st.columns(2)
    for i, tag in enumerate(results):
        with tag_cols[i % 2]:
            with st.container(border=True):
                st.markdown(
                    tag.as_html_span(additional_style="font-size: 1.2em;"),
                    unsafe_allow_html=True,
                )
                new_name = st.text_input("Name", tag.name)
                if new_name != tag.name:
                    tag.name = new_name
                    st.rerun()
                new_color = st.color_picker("Color", tag.color)
                if new_color != tag.color:
                    tag.color = new_color
                    st.rerun()
                with st.popover("Delete"):
                    st.write("Are you sure you want to delete this tag?")
                    if st.button("Yes, delete", key=f"delete-tag-{tag.id}"):
                        delete_tag(tag)
                        st.rerun()
