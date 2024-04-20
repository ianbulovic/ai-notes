import streamlit as st
from src.tag import load_tags, delete_tag


def tag_manager():
    with st.container():
        st.header("Manage Tags")
        search_query = st.text_input("Search tags", key="tag-search")
        results = load_tags()
        if search_query:
            results = [
                tag for tag in results if search_query.lower() in tag.name.lower()
            ]
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
