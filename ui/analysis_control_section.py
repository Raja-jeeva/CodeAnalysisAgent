import streamlit as st

MODEL_OPTIONS = [
    "GPT-4o",
    "Claude 3.5 Sonnet",
    "Local Llama 3",
]


def render_analysis_controls():
    """
    Renders the analysis control section with model selection, API key, and start button.
    Returns (model_name, api_key, start_clicked).
    """
    st.subheader("Analysis Control Section")
    model_name = st.selectbox("Select LLM Model", MODEL_OPTIONS, index=0)
    api_key = st.text_input("API Key (if required)", value="", type="password", help="Enter your API key for the selected provider if needed.")
    start_clicked = st.button("Start Analysis", type="primary")
    return model_name, api_key, start_clicked
