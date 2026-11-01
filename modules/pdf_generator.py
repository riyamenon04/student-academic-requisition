from pathlib import Path
from datetime import date
import textwrap

import pymupdf  # PyMuPDF

# Coordinates are in PDF points and are mapped to the supplied A4 institute template.
# Do not change the template PDF without recalibrating these positions.
APPLICATION_LABELS = {
    "Bonafide": "Bonafide",
    "Student Certificate": "Student Certificate",
    "Scholarship": "Scholarship",
    "NOC": "NOC",
    "Academic Permission": "Academic Permission",
    "Examination": "Examination",
    "Internship": "Internship",
    "Placement": "Placement",
    "Other Request": "Other request",
}


def _insert(page, point, text, size=9.5):
    if text:
        page.insert_text(point, str(text), fontname="helv", fontsize=size, color=(0, 0, 0), overlay=True)


def _draw_check(page, rect):
    x0, y0, x1, y1 = rect
    page.draw_line((x0 + 2.5, y0 + 6.5), (x0 + 5.5, y0 + 9.5), color=(0, 0, 0), width=1.2, overlay=True)
    page.draw_line((x0 + 5.5, y0 + 9.5), (x1 - 2, y0 + 2.5), color=(0, 0, 0), width=1.2, overlay=True)


def _wrap_purpose(text, max_chars=58, max_lines=3):
    lines = textwrap.wrap(text, width=max_chars, break_long_words=True, break_on_hyphens=True)
    return lines[:max_lines]


def generate_requisition_pdf(data: dict, template_path: Path, output_path: Path) -> Path:
    if not Path(template_path).exists():
        raise FileNotFoundError(f"Official PDF template not found: {template_path}")

    document = pymupdf.open(template_path)
    page = document[0]
    submitted_date = date.fromisoformat(data["submission_date"]).strftime("%d/%m/%Y")

    # Header fields. The original form leaves a narrow space for the department name;
    # shrink the text to fit that space without crossing into Department Outward No.
    department_font = pymupdf.Font("helv")
    department_width = department_font.text_length(data["department"], fontsize=9)
    department_size = min(9, 84 / department_width * 9) if department_width else 9
    department_size = max(5.2, department_size)
    _insert(page, (185, 122), data["department"], department_size)
    _insert(page, (505, 122), submitted_date, 7.5)

    # Student details.
    _insert(page, (145, 225), data["student_name"], 9.5)
    _insert(page, (96, 251), data["roll_number"], 9)
    _insert(page, (246, 251), data["semester"], 9)
    _insert(page, (330, 251), data["division"], 9)
    contact = f"{data['email']} / {data['mobile']}"
    _insert(page, (132, 282), contact, 8.5)

    # Mark the selected option in the existing printed application-type list.
    selected_label = APPLICATION_LABELS[data["application_type"]]
    matches = page.search_for(selected_label)
    if matches:
        box = matches[0]
        page.draw_rect(pymupdf.Rect(box.x0 - 1.5, box.y0 - 1.2, box.x1 + 1.5, box.y1 + 1.2), color=(0, 0, 0), width=0.8, overlay=True)

    # Purpose area: first line starts after the printed section heading; remaining lines use the existing ruled area.
    purpose_lines = _wrap_purpose(data["purpose"])
    if purpose_lines:
        _insert(page, (258, 360), purpose_lines[0], 8.5)
    if len(purpose_lines) > 1:
        _insert(page, (52, 382), purpose_lines[1], 8.5)
    if len(purpose_lines) > 2:
        _insert(page, (52, 408), purpose_lines[2], 8.5)

    # Supporting documents: mark the existing Yes/No boxes.
    if data["documents_attached"] == "Yes":
        _draw_check(page, (158.2, 451.2, 172.2, 463.1))
    else:
        _draw_check(page, (201.9, 451.3, 215.9, 463.2))
    _insert(page, (210, 484), data.get("document_names", ""), 8.5)

    # Date fields on the student section. Student signature line remains blank.
    _insert(page, (290, 581), submitted_date, 8.5)

    # All institute-use fields and signatures are deliberately left blank.
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(output_path, garbage=4, deflate=True)
    document.close()
    return output_path
