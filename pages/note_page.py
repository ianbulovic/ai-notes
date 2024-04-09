import streamlit as st
from src.note import Note, ValidationError
from src.tag import Tag, load_tags
from src.nlp import summarize_note, start_conversation_about_note, transcribe_wav
from src.utils import smart_datetime_string
from autosize_textarea import autosize_textarea

if "current_note" not in st.session_state:
    st.switch_page("homepage.py")

note: Note = st.session_state["current_note"]

st.set_page_config(page_title=f"{note.title} - AI Notes", page_icon="📝")

if "note_id" not in st.session_state or st.session_state["note_id"] != note.id:
    st.session_state["note_id"] = note.id
    st.session_state["conversation"] = start_conversation_about_note(note)


st.write('<span class="title-input-marker"/>', unsafe_allow_html=True)
new_title = st.text_input(
    "Title",
    value=note.title,
    label_visibility="collapsed",
    key=f"note-title",
)
# Add css to make title input bigger
st.markdown(
    """
<style>
    .element-container:has(.title-input-marker) + div input {
        font-size: 2.5em; 
    }
</style>""",
    unsafe_allow_html=True,
)


# an error might occur if the title is invalid or already exists
title_error_container = st.empty()

summary_container = st.empty()
if note.summary:
    with summary_container:
        with st.expander("Summary", expanded=True):
            st.write(note.summary)

if note.audio_file:
    st.audio(note.audio_file)
    transcribe_button_color = "primary" if not note.content else "secondary"
    if st.button("Transcribe", type=transcribe_button_color, use_container_width=True):
        with st.spinner("Transcribing..."):
            transcription = transcribe_wav(note.audio_file)
            note.content = transcription
            st.session_state["conversation"] = start_conversation_about_note(note)

raw, markdown = st.tabs(tabs=["Raw", "Markdown"])

with raw:
    note.content = autosize_textarea(value=note.content, key=f"note-content")

with markdown:
    st.markdown(note.content, unsafe_allow_html=True)

try:
    if new_title != note.title:
        note.title = new_title
        st.rerun()
except ValueError:
    with title_error_container:
        st.error(
            f"A note called '{new_title}' already exists. Using '{note.title}' instead."
        )
except ValidationError:
    with title_error_container:
        st.error(
            f"'{new_title}' is not a valid filename. Using '{note.title}' instead."
        )


with st.sidebar:
    st.page_link(
        "homepage.py", label="Back to Notes", icon="🏠", use_container_width=True
    )

    info, actions, chat = st.tabs(tabs=["Info", "Actions", "Chat"])

    with info:
        st.header(f"{note.title}")
        st.write(f"__Created:__ {smart_datetime_string(note.created)}")
        st.write(f"__Last modified:__ {smart_datetime_string(note.last_modified)}")
        st.write(f"__Last opened:__ {smart_datetime_string(note.last_opened)}")
        n_words = len(note.content.split())
        n_chars = len(note.content)
        st.write(f"{n_words} words, {n_chars} characters")
        st.divider()
        st.subheader("Tags:")
        tag_cols = st.columns(3)
        for i, tag in enumerate(note.tags):
            with tag_cols[i % 3]:
                st.write(tag.name)

        with st.popover("Add Tag"):
            existing_tags = load_tags()
            if existing_tags:
                st.selectbox(
                    "Select a tag",
                    options=[tag.name for tag in existing_tags],
                    key="tag-select",
                )
            st.text_input("New tag name", key="new-tag-name")

    with actions:
        st.header("Actions")
        summarize_button = st.button(
            "Summarize Content",
            type="secondary",
            key=f"note-summarize-button",
            use_container_width=True,
            help="Summarize the content of the note.",
        )

        if summarize_button:
            with st.spinner("Summarizing..."):
                summary = summarize_note(note)
                note.summary = summary
                with summary_container:
                    with st.expander("Summary", expanded=True):
                        st.write(note.summary)

        if note.summary:
            clear_summary_button = st.button(
                "Clear Summary",
                type="secondary",
                key=f"clear-summary-button",
                use_container_width=True,
                help="Summarize the content of the note.",
            )
            if clear_summary_button:
                note.summary = None
                st.rerun()

        with st.popover(
            "Delete Note", help="Delete this note.", use_container_width=True
        ):
            st.text("Are you sure you want to delete this note?")
            st.text("(This can't be undone!)")
            if st.button(
                "Yes, delete",
                key="delete-note",
                type="primary",
                use_container_width=True,
            ):
                note.delete()
                del st.session_state["current_note"]
                st.switch_page("homepage.py")

    with chat:
        conversation = st.session_state["conversation"]
        messages_area = st.container(height=500, border=True)
        # skip the system message and the first user message
        for message in conversation.messages[2:]:
            with messages_area:
                if message["role"] == "user":
                    st.chat_message("user").write(message["content"])
                elif message["role"] == "assistant":
                    st.chat_message("assistant").write(message["content"])
        question = st.chat_input("Ask a question...")
        if question:
            with messages_area:
                st.chat_message("user").write(question)
                with st.spinner("Thinking..."):
                    conversation.add_message("user", question)
                    response = conversation.get_response()
                    st.chat_message("assistant").write(response)
