import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "requisitions.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS requisitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department TEXT NOT NULL,
                student_name TEXT NOT NULL,
                roll_number TEXT NOT NULL,
                semester TEXT NOT NULL,
                division TEXT NOT NULL,
                email TEXT NOT NULL,
                mobile TEXT NOT NULL,
                application_type TEXT NOT NULL,
                purpose TEXT NOT NULL,
                documents_attached TEXT NOT NULL,
                document_names TEXT,
                submission_date TEXT NOT NULL,
                pdf_filename TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )


def save_requisition(data: dict, pdf_filename: str) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """INSERT INTO requisitions (
                department, student_name, roll_number, semester, division,
                email, mobile, application_type, purpose, documents_attached,
                document_names, submission_date, pdf_filename
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["department"], data["student_name"], data["roll_number"],
                data["semester"], data["division"], data["email"], data["mobile"],
                data["application_type"], data["purpose"], data["documents_attached"],
                data["document_names"], data["submission_date"], pdf_filename,
            ),
        )
        return cursor.lastrowid
