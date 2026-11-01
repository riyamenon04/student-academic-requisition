import re

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$")


def validate_submission(data: dict, declaration_accepted: bool) -> list[str]:
    """Return validation errors. An empty list means the submission is valid."""
    errors = []
    required_fields = {
        "Name of Department": data.get("department", ""),
        "Student Name": data.get("student_name", ""),
        "Roll Number": data.get("roll_number", ""),
        "Semester": data.get("semester", ""),
        "Division": data.get("division", ""),
        "Email Address": data.get("email", ""),
        "Mobile Number": data.get("mobile", ""),
        "Purpose / Brief Details": data.get("purpose", ""),
    }
    for label, value in required_fields.items():
        if not str(value).strip():
            errors.append(f"{label} is mandatory.")

    email = data.get("email", "").strip()
    if email and not EMAIL_PATTERN.fullmatch(email):
        errors.append("Enter a valid email address.")

    mobile = data.get("mobile", "").strip()
    if mobile and (not mobile.isdigit() or len(mobile) != 10):
        errors.append("Enter a valid 10-digit mobile number using digits only.")

    if data.get("documents_attached") == "Yes" and not data.get("document_names", "").strip():
        errors.append("Enter the name of the supporting document(s), or select No.")

    if not declaration_accepted:
        errors.append("You must accept the student declaration before generating the PDF.")

    return errors
