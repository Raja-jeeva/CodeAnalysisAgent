import streamlit as st


def render_output_section(report_text: str):
    """
    Renders the output & export section.
    Returns booleans (export_txt_clicked, export_pdf_clicked).
    """
    st.subheader("Output & Export Section")
    if not report_text:
        st.info("No report generated yet. Start the analysis to see results.")
    report_text_box = st.text_area("Verification Report", value=report_text, height=400)

    col_a, col_b = st.columns(2)
    with col_a:
        export_txt_clicked = st.button("Export as .txt")
    with col_b:
        export_pdf_clicked = st.button("Export as .pdf")

    return export_txt_clicked, export_pdf_clicked

