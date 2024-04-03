import os
from typing import Literal
from numpy import rec
import streamlit as st
import streamlit.components.v1 as components

from io import BytesIO
from base64 import b64decode
from pydub import AudioSegment

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "audiorecorder",
        url="http://localhost:3002",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("audiorecorder", path=build_dir)


def audiorecorder(
    start_label="Start recording",
    stop_label="Stop recording",
    type: Literal["primary", "secondary"] = "primary",
    use_container_width=False,
    disabled=False,
    key=None,
):
    st.session_state["recording"] = st.session_state.get("recording", False)
    if not st.session_state["recording"]:
        if st.button(
            start_label,
            type=type,
            use_container_width=use_container_width,
            disabled=disabled,
            key="start-recording",
        ):
            st.session_state["recording"] = True
            st.rerun()
    else:
        if st.button(
            stop_label,
            type=type,
            use_container_width=use_container_width,
            key="stop-recording",
        ):
            st.session_state["recording"] = False
            st.rerun()

    base64_audio = _component_func(
        recording=st.session_state["recording"],
        key=key,
        default=b"",
    )

    audio_segment = AudioSegment.empty()
    if len(base64_audio) > 0:
        # Firefox and Chrome handle webm but Safari doesn't, so we let pydub/ffmpeg figure out the format
        audio_segment = AudioSegment.from_file(BytesIO(b64decode(base64_audio)))
        # audio_segment = AudioSegment.from_file(BytesIO(b64decode(base64_audio)), format="webm")
    return audio_segment
