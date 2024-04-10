import os
import streamlit as st
from audiorecorder import audiorecorder
from src.note import NOTES_DIR, Note

if "current_note" not in st.session_state:
    st.switch_page("homepage.py")

note: Note = st.session_state["current_note"]

st.set_page_config(page_title="Record Voice Note - AI Notes", page_icon="📝")

st.markdown(
    "<h1 style='text-align: center'>Record Voice Note</h1>",
    unsafe_allow_html=True,
)

audio = audiorecorder(
    "Click to start recording",
    "Click to stop recording",
    type="secondary",
    use_container_width=True,
    key=f"record-audio-button",
)
if len(audio) > 0:
    audio_dir = os.path.join(NOTES_DIR, "audio")
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    audio_path = os.path.join(audio_dir, f"{note.title}.wav")

    # Format audio for whisper.cpp transcription
    audio = audio.set_frame_rate(16000)
    audio = audio.set_sample_width(2)
    audio.export(audio_path, format="wav")

    note.audio_file = audio_path
    st.switch_page("pages/note_page.py")
