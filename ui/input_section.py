import streamlit as st


def render_input_section():
    """
    Renders the input section with a file uploader for .docx and a text input for source directory path.
    Returns (uploaded_docx, source_dir).
    """
    st.subheader("Input Section")
    uploaded_docx = st.file_uploader("Upload Requirements Document (.docx)", type=["docx"], help="Upload a Microsoft Word document containing requirements.")
    source_dir = st.text_input("Source Code Directory Path", value="", help="Enter the path to the root directory of your source code.")
    return uploaded_docx, source_dir