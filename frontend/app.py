
import streamlit as st
import requests
import pdfplumber
import docx2txt


def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == "txt":
        return uploaded_file.read().decode("utf-8")

    elif file_type == "pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

    elif file_type == "docx":
        return docx2txt.process(uploaded_file)

    else:
        st.error("Unsupported file format. Please upload a .txt, .pdf, or .docx file.")
        return ""

# ---- Streamlit UI ----

st.set_page_config(page_title="Katalyst", layout="centered")
st.title("Katalyst")

# File Upload Option
uploaded_file = st.file_uploader("Upload your resume file (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"])

resume_text = ""
if uploaded_file:
    resume_text = extract_text_from_file(uploaded_file)
    if resume_text:
        st.success("Resume file uploaded and parsed successfully.")

# Text area (optional for editing or if no file uploaded)
resume_text = st.text_area("Or paste your resume text below", value=resume_text, height=200)

# Job Description URL input
job_url = st.text_input("Paste the URL of your target job description")

# Output placeholder
output_placeholder = st.empty()

# Trigger Button
if st.button("Generate My Path"):
    if not resume_text.strip() or not job_url.strip():
        st.warning("Please provide both a resume and job description URL.")
    else:
        with st.spinner("Analyzing skill gap..."):
            try:
                output_placeholder.markdown("⏳ *Analyzing skill gap...*")

                response = requests.post(
                    "http://backend:8000/generate_roadmap",
                    json={
                        "resume_text": resume_text,
                        "job_url": job_url
                    },
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    markdown_output = data.get("roadmap_markdown", "")
                    if markdown_output:
                        output_placeholder.markdown(markdown_output)
                    else:
                        output_placeholder.error("No roadmap returned from backend.")
                elif response.status_code == 400:
                    output_placeholder.error("Invalid input. Please check your job URL.")
                else:
                    output_placeholder.error("Unexpected error occurred. Try again later.")
            except requests.exceptions.RequestException as e:
                output_placeholder.error(f"Failed to connect to backend: {e}")
