import os
import sys
import traceback
import streamlit as st

# Ensure local package imports work when running from root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from modules.logger import get_logger
from modules.file_parser import parse_requirements, read_source_code, build_structured_prompt
from modules.llm_integration import analyze_with_llm
from modules.report_generator import generate_report_text, export_to_txt, export_to_pdf
from ui.input_section import render_input_section
from ui.analysis_control_section import render_analysis_controls
from ui.output_section import render_output_section

logger = get_logger(__name__)

st.set_page_config(page_title="Requirements Verifier", layout="wide")
st.title("Requirements Verification and Code Analysis")

# Ensure output directory exists
os.makedirs(os.path.join(PROJECT_ROOT, "output"), exist_ok=True)

# Initialize session state
if "report_text" not in st.session_state:
    st.session_state["report_text"] = ""
if "last_matrix" not in st.session_state:
    st.session_state["last_matrix"] = {}
if "analysis_ready" not in st.session_state:
    st.session_state["analysis_ready"] = False

with st.sidebar:
    st.markdown("### Application Info")
    st.write("This tool verifies software requirements against source code using LLMs.")
    st.write("Select your model provider (GPT-4o, Claude 3.5 Sonnet, or Local Llama 3). If no API key is provided or the provider is unavailable, a mock analysis will be performed.")
    st.write("Generated reports are saved to the 'output' folder.")

# Layout columns for sections
col1, col2 = st.columns(2)

with col1:
    uploaded_docx, source_dir = render_input_section()

with col2:
    model_name, api_key, start_clicked = render_analysis_controls()

# Start analysis process
if start_clicked:
    if uploaded_docx is None:
        st.error("Please upload a .docx requirements document.")
    elif not source_dir:
        st.error("Please enter a valid source code directory path.")
    elif not os.path.isdir(source_dir):
        st.error("The provided source code directory does not exist.")
    else:
        try:
            with st.spinner("Parsing requirements and source code..."):
                requirements = parse_requirements(uploaded_docx)
                source_files = read_source_code(source_dir)
                prompt = build_structured_prompt(requirements, source_files)

            with st.spinner(f"Analyzing with {model_name}..."):
                llm_result = analyze_with_llm(prompt, model_name, api_key)

            with st.spinner("Generating report..."):
                report_text = generate_report_text(
                    summary=llm_result.get("summary", ""),
                    traceability_matrix=llm_result.get("traceability_matrix", {}),
                    missing_requirements=llm_result.get("missing_requirements", []),
                    suggestions=llm_result.get("suggestions", []),
                    detailed_analysis=llm_result.get("detailed_analysis", "")
                )
                st.session_state["report_text"] = report_text
                st.session_state["last_matrix"] = llm_result.get("traceability_matrix", {})
                st.session_state["analysis_ready"] = True
            st.success("Analysis completed. Review the report below.")
        except Exception as e:
            logger.exception("Analysis failed: %s", e)
            st.error("An error occurred during analysis. Check output/app.log for details.")

# Output & Export Section
export_txt_clicked, export_pdf_clicked = render_output_section(st.session_state.get("report_text", ""))

if export_txt_clicked:
    try:
        saved_path = export_to_txt(st.session_state.get("report_text", ""), os.path.join(PROJECT_ROOT, "output", "verification_report.txt"))
        st.success(f"Report exported to TXT: {saved_path}")
    except Exception as e:
        logger.exception("Failed to export TXT: %s", e)
        st.error("Failed to export TXT.")

if export_pdf_clicked:
    try:
        saved_path = export_to_pdf(st.session_state.get("report_text", ""), os.path.join(PROJECT_ROOT, "output", "verification_report.pdf"))
        st.success(f"Report exported to PDF: {saved_path}")
    except Exception as e:
        logger.exception("Failed to export PDF: %s", e)
        st.error("Failed to export PDF.")