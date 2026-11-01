import re
from datetime import date
from pathlib import Path

import streamlit as st

from database.db import initialize_database, save_requisition
from modules.pdf_generator import generate_requisition_pdf
from modules.validation import validate_submission

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "generated_pdfs"
TEMPLATE_PATH = BASE_DIR / "templates" / "official_requisition_form.pdf"

st.set_page_config(page_title="Student Academic Requisition Form", page_icon="📄", layout="centered")
initialize_database()

st.title("Student Academic Requisition Form")
st.caption("Complete the form below to generate a PDF using the institute-provided requisition form.")
st.info("Processing time: Normally within 4 working days after receiving the completed form and all required supporting documents.")

APPLICATION_TYPES = [
    "Bonafide",
    "Student Certificate",
    "Scholarship",
    "NOC",
    "Academic Permission",
    "Examination",
    "Internship",
    "Placement",
    "Other Request",
]

with st.form("requisition_form"):
    st.subheader("Student Details")
    department = st.text_input("Name of Department *")
    student_name = st.text_input("Student Name *")
    c1, c2, c3 = st.columns(3)
    with c1:
        roll_number = st.text_input("Roll Number *")
    with c2:
        semester = st.text_input("Semester *")
    with c3:
        division = st.text_input("Division *")
    email = st.text_input("Email Address *")
    mobile = st.text_input("Mobile Number *", placeholder="10-digit mobile number")

    application_type = st.selectbox("Application Type *", APPLICATION_TYPES)
    purpose = st.text_area("Purpose / Brief Details of Request *", height=120, max_chars=500)

    st.subheader("Supporting Documents")
    documents_attached = st.radio("Are supporting documents attached? *", ["Yes", "No"], horizontal=True)
    document_names = st.text_input("Name of supporting document(s)", disabled=(documents_attached == "No"))

    submission_date = st.date_input("Date *", value=date.today())

    st.subheader("Student Declaration")
    declaration = (
        "I certify that the information provided above is correct and that the request is being submitted for academic "
        "purposes. I understand that the request will be processed as per applicable Institute/University rules and "
        "within the stipulated processing time."
    )
    st.write(declaration)
    declaration_accepted = st.checkbox("I confirm the student declaration stated above. *")

    submitted = st.form_submit_button("Generate PDF", type="primary", use_container_width=True)

if submitted:
    data = {
        "department": department.strip(),
        "student_name": student_name.strip(),
        "roll_number": roll_number.strip(),
        "semester": semester.strip(),
        "division": division.strip(),
        "email": email.strip(),
        "mobile": mobile.strip(),
        "application_type": application_type,
        "purpose": purpose.strip(),
        "documents_attached": documents_attached,
        "document_names": document_names.strip() if documents_attached == "Yes" else "",
        "submission_date": submission_date.isoformat(),
    }
    errors = validate_submission(data, declaration_accepted)
    if errors:
        for error in errors:
            st.error(error)
    else:
        try:
            OUTPUT_DIR.mkdir(exist_ok=True)
            safe_roll = re.sub(r"[^A-Za-z0-9_-]", "_", data["roll_number"])
            safe_name = re.sub(r"[^A-Za-z0-9_-]", "_", data["student_name"].replace(" ", "_"))
            filename = f"Requisition_{safe_roll}_{safe_name}.pdf"
            output_path = OUTPUT_DIR / filename
            generate_requisition_pdf(data, TEMPLATE_PATH, output_path)
            requisition_id = save_requisition(data, filename)
            st.session_state["generated_pdf"] = str(output_path)
            st.session_state["generated_filename"] = filename
            st.session_state["requisition_id"] = requisition_id
            st.success(f"PDF generated successfully. Requisition record ID: {requisition_id}")
        except Exception as exc:
            st.error(f"Could not generate the PDF: {exc}")

if st.session_state.get("generated_pdf"):
    generated_path = Path(st.session_state["generated_pdf"])
    if generated_path.exists():
        st.download_button(
            "Download PDF",
            data=generated_path.read_bytes(),
            file_name=st.session_state["generated_filename"],
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
