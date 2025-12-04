import os
from typing import Dict, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from .logger import get_logger

logger = get_logger(__name__)

def _traceability_table_data(matrix: Dict[str, str]) -> List[List[str]]:
    headers = ["Requirement ID", "Status"]
    rows = [[rid, status] for rid, status in matrix.items()]
    return [headers] + rows

def generate_report_text(summary: str, traceability_matrix: Dict[str, str], missing_requirements: List[str], suggestions: List[str], detailed_analysis: str) -> str:
    lines = []
    lines.append("Requirements Verification Report")
    lines.append("=" * 35)
    lines.append("")
    lines.append("Summary:")
    lines.append(summary or "No summary provided.")
    lines.append("")
    lines.append("Traceability Matrix:")
    if traceability_matrix:
        for rid, status in traceability_matrix.items():
            lines.append(f"- {rid}: {status}")
    else:
        lines.append("(No traceability data)")
    lines.append("")
    lines.append("Missing/Unimplemented Requirements:")
    if missing_requirements:
        for rid in missing_requirements:
            lines.append(f"- {rid}")
    else:
        lines.append("(None)")
    lines.append("")
    lines.append("Actionable Suggestions:")
    if suggestions:
        for s in suggestions:
            lines.append(f"- {s}")
    else:
        lines.append("(No suggestions)")
    lines.append("")
    lines.append("Detailed Analysis:")
    lines.append(detailed_analysis or "(No detailed analysis)")
    lines.append("")

    return "\n".join(lines)

def export_to_txt(content: str, filepath: str) -> str:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info("TXT report saved: %s", filepath)
    return filepath

def export_to_pdf(content: str, filepath: str) -> str:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    styles = getSampleStyleSheet()
    story = []

    # Split content into sections for better PDF layout
    for line in content.splitlines():
        if line.strip() == "":
            story.append(Spacer(1, 8))
            continue
        if line.endswith(":") and not line.startswith("-"):
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"<b>{line}</b>", styles["Heading4"]))
            story.append(Spacer(1, 4))
            continue
        story.append(Paragraph(line.replace(" ", "&nbsp;"), styles["BodyText"]))

    # Try to extract a table from the content
    # This is a simple heuristic; the actual matrix is textual in the content.
    # Users can rely on the text; optional future improvement: pass structured data.

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    doc.build(story)
    logger.info("PDF report saved: %s", filepath)
    return filepath
