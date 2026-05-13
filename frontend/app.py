import sys
sys.path.insert(0, '.')

import streamlit as st

st.set_page_config(
    page_title="Educational Packet Analyzer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state["page"] = "upload"

    page = st.session_state.get("page", "upload")

    if page == "upload":
        from frontend.pages.upload_page import render_upload_page
        render_upload_page()

    elif page == "analysis":
        from frontend.pages.analysis_page import render_analysis_page
        render_analysis_page()

    else:
        st.error(f"Unknown page: {page}")
        st.session_state["page"] = "upload"
        st.rerun()


if __name__ == "__main__":
    main()
