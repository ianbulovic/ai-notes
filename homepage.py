from datetime import datetime
import streamlit as st
from src.note import Note, load_notes

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

st.divider()

st.header("My Notes")

l, r = st.columns([3, 1])
with l:
    search_query = st.text_input("Search", key="search")
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
        if st.button(note.title, key=note.title, use_container_width=True):
            st.session_state["current_note"] = note
            note.last_opened = datetime.now()
            note.save()
            st.switch_page("pages/note_page.py")
