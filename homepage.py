import streamlit as st

from src.note import Note
import ui

if "current_note" in st.session_state:
    del st.session_state["current_note"]

st.set_page_config(page_title="My Notes - AI Notes", page_icon="📝", layout="wide")

st.markdown(
    "<h1 style='text-align: center'>AI Notes</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    .element-container:has(style){
        display: none;
    }
    #button-after {
        display: none;
    }
    .element-container:has(#button-after) {
        display: none;
    }
    .element-container:has(#button-after) + div button div p {
        font-size: 1.5em !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

_, note_creation_area, _ = st.columns([1, 2, 1])
with note_creation_area:
    with st.container(border=True):
        new_note_col, voice_note_col = st.columns(2)
with new_note_col:
    st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
    if st.button("New Note :memo:", type="primary", use_container_width=True):
        note = Note()
        st.session_state["current_note"] = note
        st.switch_page("pages/note_page.py")
with voice_note_col:
    st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
    if st.button(
        "New Voice Note :studio_microphone:", type="primary", use_container_width=True
    ):
        note = Note()
        st.session_state["current_note"] = note
        st.switch_page("pages/record_voicenote.py")

view_notes_tab, manage_tags_tab = st.tabs(["View Notes", "Manage Tags"])

with view_notes_tab:
    ui.note_search()

with manage_tags_tab:
    ui.tag_manager()
