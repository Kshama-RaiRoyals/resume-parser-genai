"""Streamlit UI for the Resume Parser API."""
import json
import os
from pathlib import Path
import streamlit as st
import requests

st.set_page_config(page_title="Resume Parser", page_icon="📄", layout="wide")
st.title("📄 Resume Parser")
st.caption("Upload a PDF/DOCX resume and extract structured information using an LLM.")

api_url = st.sidebar.text_input("FastAPI base URL", value=os.getenv("API_BASE_URL", "http://127.0.0.1:8000")).rstrip("/")
st.sidebar.markdown("API docs: [Open Swagger UI](http://127.0.0.1:8000/docs)")

uploaded = st.file_uploader("Choose a resume", type=["pdf", "docx"])
if uploaded is not None:
    st.info(f"Selected: {uploaded.name} · {uploaded.size:,} bytes")
    if st.button("Extract Resume Information", type="primary"):
        if uploaded.size == 0:
            st.error("The uploaded file is empty.")
        elif uploaded.size > 10 * 1024 * 1024:
            st.error("File exceeds the 10 MB limit.")
        else:
            with st.spinner("Reading resume and extracting information..."):
                try:
                    response = requests.post(
                        f"{api_url}/api/upload",
                        files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")},
                        timeout=120,
                    )
                    if response.status_code >= 400:
                        try:
                            detail = response.json().get("detail", response.text)
                        except Exception:
                            detail = response.text
                        st.error(f"API error ({response.status_code}): {detail}")
                    else:
                        payload = response.json()
                        data = payload["extracted_data"]
                        st.success(f"Extraction complete · mode: {payload.get('mode', 'llm')} · ID: {payload['document_id']}")
                        contact = data.get("contact_information", {})
                        st.subheader("Contact Information")
                        c1, c2 = st.columns(2)
                        c1.write(f"**Name:** {contact.get('name') or 'Not found'}")
                        c1.write(f"**Email:** {contact.get('email') or 'Not found'}")
                        c2.write(f"**Phone:** {contact.get('phone') or 'Not found'}")
                        c2.write(f"**Location:** {contact.get('location') or 'Not found'}")

                        st.subheader("Professional Summary / Objective")
                        st.write(data.get("professional_summary") or "Not found")

                        st.subheader("Work Experience")
                        work = data.get("work_experience", [])
                        if work:
                            for i, item in enumerate(work, 1):
                                with st.expander(f"{i}. {item.get('role') or 'Role not specified'} — {item.get('company') or 'Company not specified'}", expanded=True):
                                    st.write(f"**Duration:** {item.get('duration') or 'Not found'}")
                                    st.write("**Responsibilities**")
                                    if item.get("responsibilities"):
                                        for responsibility in item["responsibilities"]:
                                            st.markdown(f"- {responsibility}")
                                    else:
                                        st.write("Not found")
                        else:
                            st.write("No work experience found.")

                        st.subheader("Education")
                        education = data.get("education", [])
                        if education:
                            st.dataframe(education, use_container_width=True, hide_index=True)
                        else:
                            st.write("No education entries found.")

                        c1, c2 = st.columns(2)
                        with c1:
                            st.subheader("Technical Skills")
                            st.write(", ".join(data.get("technical_skills", [])) or "Not found")
                        with c2:
                            st.subheader("Soft Skills")
                            st.write(", ".join(data.get("soft_skills", [])) or "Not found")
                        st.subheader("Certifications")
                        certs = data.get("certifications", [])
                        st.write(", ".join(certs) if certs else "Not found")
                        st.download_button(
                            "Download extracted JSON",
                            data=json.dumps(payload, indent=2, ensure_ascii=False),
                            file_name=f"resume_{payload['document_id']}.json",
                            mime="application/json",
                        )
                except requests.RequestException as exc:
                    st.error(f"Could not connect to the FastAPI service at {api_url}. Start the API and try again. Details: {exc}")
