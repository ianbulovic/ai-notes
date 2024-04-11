from turtle import up
import streamlit as st
from src.note import Note, ValidationError
from src.tag import Tag, load_tags
from src.nlp import (
    summarize_note,
    start_conversation_about_note,
    transcribe_wav,
    update_note_embedding,
)
from src.utils import generate_random_hex_color, smart_datetime_string
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
    new_content = autosize_textarea(value=note.content, key=f"note-content")
    if new_content != note.content:
        note.content = new_content
        update_note_embedding(note)


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
        st.divider()
        st.subheader("Tags")
        with st.popover(
            "Edit Tags",
            help="Add or remove tags from this note.",
            use_container_width=True,
        ):
            use_existing, create_new, remove = st.tabs(
                ["Add an existing tag", "Create a new tag", "Remove tags"]
            )
            with use_existing:
                existing_tags = load_tags()
                if existing_tags:
                    existing_name = st.selectbox(
                        "Select a tag",
                        options=[tag.name for tag in existing_tags],
                        key="tag-select",
                    )
                    if st.button("Add Tag", use_container_width=True, type="primary"):
                        tag = next(
                            (t for t in existing_tags if t.name == existing_name), None
                        )
                        if tag:
                            note.add_tag(tag)
                            st.write(f"Added tag '{tag.name}'")
            with create_new:
                new_tag_name = st.text_input("New tag name", key="new-tag-name")
                name_error_container = st.empty()
                if f"tag-color-picker-state" not in st.session_state:
                    st.session_state[f"tag-color-picker-state"] = (
                        generate_random_hex_color()
                    )
                new_tag_color = st.color_picker(
                    "Tag color",
                    key=f"tag-color-picker-state-{note.id}",
                    value=st.session_state[f"tag-color-picker-state"],
                )
                st.session_state[f"tag-color-picker-state"] = new_tag_color
                submitted = st.button(
                    "Add Tag",
                    use_container_width=True,
                    type="primary",
                    key=f"add-tag-{note.id}",
                )
                if submitted:
                    if not new_tag_name:
                        with name_error_container:
                            st.error("Tag name can't be empty.")
                    else:
                        new_tag = Tag(name=new_tag_name, color=new_tag_color)
                        note.add_tag(new_tag)
                        st.write(f"Added tag '{new_tag_name}'")
            with remove:
                for tag in note.tags:
                    with st.container():
                        st.markdown(
                            f'<span class="remove-tag-button-{tag.id}"/>',
                            unsafe_allow_html=True,
                        )
                        if st.button(
                            f"{tag.name}",
                            key=f"remove-tag-{tag.id}",
                            type="secondary",
                            help=f"Remove the tag {tag.name} from this note.",
                        ):
                            note.remove_tag(tag)
                            st.rerun()
                        st.markdown(
                            f"""
                        <style>
                            .element-container:has(.remove-tag-button-{tag.id}) + div button {{
                                background-color: {tag.color};
                                color: {tag.foreground_color()};
                            }}
                        </style>""",
                            unsafe_allow_html=True,
                        )
        for i, tag in enumerate(note.tags):
            st.markdown(tag.as_html_span(), unsafe_allow_html=True)
        st.divider()
        st.write(f"__Created:__ {smart_datetime_string(note.created)}")
        st.write(f"__Last modified:__ {smart_datetime_string(note.last_modified)}")
        st.write(f"__Last opened:__ {smart_datetime_string(note.last_opened)}")
        n_words = len(note.content.split())
        n_chars = len(note.content)
        st.write(f"{n_words} words, {n_chars} characters")

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
