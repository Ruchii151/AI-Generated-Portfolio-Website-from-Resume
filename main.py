import streamlit as st
from dotenv import load_dotenv
import os
import io
import zipfile

from langchain_google_genai import ChatGoogleGenerativeAI
from PyPDF2 import PdfReader
from docx import Document

# ---------- ENV / CONFIG ----------
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("gemini")

st.set_page_config(
    page_title="AI Portfolio from Resume",
    page_icon="👽",
    layout="wide",
)

# ---------- HELPERS: RESUME PARSING ----------

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text_chunks = []
    for page in reader.pages:
        text_chunks.append(page.extract_text() or "")
    return "\n".join(text_chunks)

def extract_text_from_docx(file_bytes: bytes) -> str:
    bio = io.BytesIO(file_bytes)
    document = Document(bio)
    return "\n".join(p.text for p in document.paragraphs)

def extract_resume_text(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    file_bytes = uploaded_file.read()
    if uploaded_file.type == "application/pdf" or uploaded_file.name.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if (
        uploaded_file.type
        in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ]
        or uploaded_file.name.lower().endswith(".docx")
    ):
        return extract_text_from_docx(file_bytes)
    return ""

# ---------- LLM MODELS ----------

def get_llm(model_name: str = "gemini-2.5-flash-lite") -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model=model_name)

# ---------- PROMPTS ----------

RESUME_TO_SPEC_SYSTEM = """
You are an expert career coach and portfolio website strategist.

Task: Read the full resume text provided by the user and produce a structured website specification
for a personal portfolio.

The output MUST be a well-structured description (not code) that clearly defines:
- Name and headline/tagline
- Short bio / about section (2–3 sentences)
- Skills (grouped by categories if possible)
- Experience (roles, companies, dates, 2–3 bullet points each)
- Projects (name, brief description, tech stack, links if given)
- Achievements / awards / certifications
- Education
- Contact info (email, phone, location, portfolio links if any)
- Design style (e.g., modern, minimal, dark/light theme, preferred colors inferred from resume if any)

Write this as a clear narrative and bullet points that an engineer could use
to design a portfolio website.
"""

SPEC_TO_WEBSITE_SYSTEM = """
You are a senior frontend engineer and UI/UX expert.

Goal:
Generate a complete, production-ready static portfolio website based ONLY on the structured website
specification provided by the user (not the raw resume).

Requirements:
- Use modern, semantic HTML5 structure (header, main, section, footer, etc.).
- Add clear sections: hero, skills, experience, projects, education, achievements, contact, and any
  extra sections mentioned in the specification.
- Ensure the layout is responsive and mobile-friendly using flexbox or CSS grid (no CSS frameworks).
- Use clean, readable class names and consistent indentation.
- Do NOT include inline CSS or inline JavaScript inside the HTML.

Styling:
- Provide all styling in a separate CSS file.
- Use a modern look with good spacing, hierarchy, and accessible color contrast.
- Import a simple Google Font (e.g., "Poppins" or "Inter") in the CSS.
- Include hover states for buttons and links.
- Respect any style or color hints present in the specification.

Behavior (JavaScript):
- Only write vanilla JavaScript.
- If there is a navbar with internal links, implement smooth scrolling.
- Add small, useful interactions if relevant (e.g., mobile nav toggle, simple fade-in animations,
  FAQ accordion, etc.).
- Do NOT use external JS libraries or frameworks.

Output format (STRICT):
Return your answer in EXACTLY this structure with no extra text, comments, or explanations:

--html--
[HTML CODE]
--html--
--css--
[CSS CODE]
--css--
--js--
[JS CODE]
--js--
"""

def build_spec_from_resume(resume_text: str) -> str:
    llm = get_llm()
    messages = [
        ("system", RESUME_TO_SPEC_SYSTEM),
        ("user", f"Here is the full resume text:\n\n{resume_text}"),
    ]
    response = llm.invoke(messages)
    return response.content

def build_website_from_spec(spec_text: str) -> dict:
    llm = get_llm()
    messages = [
        ("system", SPEC_TO_WEBSITE_SYSTEM),
        ("user", f"Here is the structured website specification:\n\n{spec_text}"),
    ]
    response = llm.invoke(messages)
    raw = response.content

    def extract_between(marker: str, text: str) -> str:
        parts = text.split(marker)
        if len(parts) < 3:
            return ""
        return parts[1].strip()

    html_code = extract_between("--html--", raw)
    css_code = extract_between("--css--", raw)
    js_code = extract_between("--js--", raw)

    return {
        "html": html_code,
        "css": css_code,
        "js": js_code,
    }

def create_zip_bytes(html: str, css: str, js: str) -> bytes:
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, mode="w") as zf:
        zf.writestr("index.html", html)
        zf.writestr("style.css", css)
        zf.writestr("script.js", js)
    mem_zip.seek(0)
    return mem_zip.read()

# ---------- PREVIEW SANITIZER ----------

def force_light_theme(html: str) -> str:
    override_css = """
    <style>
    body, html {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    * {
        color: inherit !important;
    }
    a {
        color: #1a73e8 !important;
    }
    </style>
    """
    return f"<!DOCTYPE html><html><head>{override_css}</head><body>{html}</body></html>"

def sanitize_html_for_preview(html: str) -> str:
    html = html.replace("<a ", '<a target="_blank" rel="noopener noreferrer" ')
    html = force_light_theme(html)
    return html

# ---------- SESSION STATE ----------
if "spec_text" not in st.session_state:
    st.session_state.spec_text = ""
if "html_code" not in st.session_state:
    st.session_state.html_code = ""
if "css_code" not in st.session_state:
    st.session_state.css_code = ""
if "js_code" not in st.session_state:
    st.session_state.js_code = ""
if "zip_bytes" not in st.session_state:
    st.session_state.zip_bytes = None

# ---------- UI LAYOUT ----------

st.title("AI-Generated Portfolio Website from Resume")
st.caption(
    "Upload your resume (PDF or DOCX) and automatically generate a multi-section portfolio website "
    "with preview and downloadable source code (HTML, CSS, JS)."
)

left, right = st.columns([1, 1])

with left:
    st.subheader("1. Upload Resume")
    uploaded_resume = st.file_uploader(
        "Upload your resume (PDF or DOCX)",
        type=["pdf", "docx"],
    )

    generate_spec_btn = st.button("Generate Website Specification", type="primary")

    if generate_spec_btn:
        if not uploaded_resume:
            st.error("Please upload a resume first.")
        else:
            with st.spinner("Extracting text and building website specification..."):
                resume_text = extract_resume_text(uploaded_resume)
                if not resume_text.strip():
                    st.error("Could not extract text from the uploaded file. Check the format.")
                else:
                    spec = build_spec_from_resume(resume_text)
                    st.session_state.spec_text = spec
            st.success("Website specification generated successfully.")

    if st.session_state.spec_text:
        st.subheader("Structured Website Specification")
        st.text_area(
            "You can optionally edit this specification before generating the website.",
            value=st.session_state.spec_text,
            height=350,
            key="spec_editor",
        )

        generate_site_btn = st.button("Generate Portfolio Website", type="secondary")

        if generate_site_btn:
            with st.spinner("Generating portfolio website (HTML, CSS, JS)..."):
                website = build_website_from_spec(st.session_state.spec_text)
                st.session_state.html_code = website["html"]
                st.session_state.css_code = website["css"]
                st.session_state.js_code = website["js"]

                if website["html"] and website["css"] and website["js"]:
                    st.session_state.zip_bytes = create_zip_bytes(
                        website["html"], website["css"], website["js"]
                    )
            st.success("Website source code generated.")

with right:
    st.subheader("2. Website Preview")
    if st.session_state.html_code:
        safe_html = sanitize_html_for_preview(st.session_state.html_code)
        st.components.v1.html(
            safe_html,
            height=600,
            scrolling=True,
        )
    else:
        st.info("Website preview will appear here after generation.")

    st.subheader("3. Download Source Code")
    if st.session_state.zip_bytes:
        st.download_button(
            "Download Website ZIP",
            data=st.session_state.zip_bytes,
            file_name="portfolio_website.zip",
            mime="application/zip",
        )
    else:
        st.caption("Generate the website to enable the download button.")

st.markdown("---")
