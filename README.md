# Resume Parser — Take-Home Assignment

A small resume parser with a FastAPI REST API and Streamlit web UI. It accepts PDF/DOCX resumes and uses an LLM to extract structured fields.

## Extracted fields
- Contact information: name, email, phone, location
- Professional summary/objective
- Work experience: company, role, duration, responsibilities
- Education: degree, institution, year
- Skills: technical and soft skills
- Certifications

## Project structure
```text
resume-parser/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── main.py
│   ├── models.py
│   ├── services/
│   │   ├── parser.py
│   │   └── llm_service.py
│   └── utils/logger.py
├── ui/streamlit_app.py
├── data/uploads/
└── tests/test_api.py
```

## Setup
Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your OpenAI API key to `.env`. The app defaults to `gpt-4o-mini`; set `OPENAI_MODEL` to another supported model if desired. Never commit `.env`.

## Run the API
From the project root:
```bash
uvicorn app.main:app --reload
```
- Swagger docs: http://127.0.0.1:8000/docs
- `POST /api/upload`: upload one PDF/DOCX resume, returns extracted JSON and a unique `document_id`.
- `GET /api/resume/{document_id}`: retrieve the parsed result; returns 404 if not found.

The API stores parsed results in memory for this take-home demo. Restarting the API clears stored results. For production, use a database and object storage.

## Run the UI
In a second terminal:
```bash
streamlit run ui/streamlit_app.py
```
Upload a PDF/DOCX and click **Extract Resume Information**. The UI displays results in organized sections and lets you download the JSON.

## Offline smoke-test mode
For a local UI/API smoke test without API credentials, set `MOCK_LLM=true` in `.env`. This mode returns a clearly labelled mock extraction and does not call an LLM; it is only for testing the app wiring. For assignment evaluation, set `MOCK_LLM=false` and provide a valid API key so actual LLM extraction is used.

## Tests
```bash
pytest -q
```
Tests use `MOCK_LLM=true` and exercise both endpoints, validation, and missing-document handling. No network/API key is needed for these tests.

## Notes
- PDF extraction uses PyMuPDF; DOCX extraction uses `python-docx`.
- Only `.pdf` and `.docx` are accepted. Files are size-limited to 10 MB.
- The prompt asks the LLM to return JSON only; Pydantic validates/normalizes the result.
- API keys are read from environment variables and are never hardcoded.
