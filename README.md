# Student Academic Requisition Form

A Python + Streamlit application that collects student requisition details, validates the submission, stores it in SQLite, and generates a PDF by filling the supplied institute form template.

## Requirements

- Python 3.10 or newer
- pip

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# On Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Official PDF template

`templates/official_requisition_form.pdf` is a PDF export of the supplied institute DOCX. The PDF generator overlays student-entered details onto this template. The original DOCX is retained in the same folder for reference.

The PDF placement coordinates in `modules/pdf_generator.py` are calibrated to this exact template export. If the institute supplies a revised form, replace the template only after checking and recalibrating the field positions.

## Data storage

Validated submissions are stored in `database/requisitions.db` (SQLite). Generated PDFs are saved in `generated_pdfs/` and can be downloaded from the app.

## Deployment note

SQLite and locally saved PDFs are suitable for a small assignment deployment. On hosting platforms with ephemeral storage, local database files may not persist across rebuilds/restarts unless persistent storage is configured.
