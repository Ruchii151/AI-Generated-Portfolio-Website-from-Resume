# AI‑Generated Portfolio Website from Resume

This project automatically converts a resume into a multi‑section personal portfolio website using LLMs and Streamlit. The app parses the uploaded resume, generates a structured website specification, and then produces production‑ready HTML, CSS, and JavaScript code that can be previewed and downloaded as a ZIP.

## Features

- Upload resume in PDF or DOCX format.
- Automatic text extraction using PyPDF2 and python‑docx.
- Two‑stage LLM pipeline:
  - LLM #1: Resume → structured portfolio specification (bio, skills, projects, etc.).
  - LLM #2: Specification → complete website code (HTML, CSS, JS).
- Live website preview inside the Streamlit UI with forced light theme for readability.  
- All links in preview open in a new tab, so the Streamlit app is never replaced.  
- One‑click download of `index.html`, `style.css`, and `script.js` as a ZIP archive.

## Architecture

### High‑Level Flow

Resume → Text Extraction → LLM #1 (Spec) → LLM #2 (Code) → Preview → ZIP Download.

### Components

- **Streamlit UI**  
  - Handles file upload, buttons, and layout.  
  - Shows the intermediate website specification and the final preview.  

- **Resume Extraction Module**  
  - `PyPDF2` for PDF pages.  
  - `python-docx` for DOCX content.
  - Normalizes extracted text into a single string.

- **LLM #1 – Resume to Specification**  
  - Input: raw resume text.  
  - Output: structured description including:
    - Name and headline.  
    - Short bio.  
    - Skills grouped by category.  
    - Experience, projects, achievements, education, and contact details.  
    - Suggested design style (modern, minimal, light/dark, colors, etc.).

- **LLM #2 – Specification to Website Code**  
  - Input: structured website specification.  
  - Output: plain code in a strict format:  
    - `--html-- ... --html--`  
    - `--css-- ... --css--`  
    - `--js-- ... --js--`  
  - HTML is semantic and responsive (header, main, section, footer).
  - CSS uses a modern layout and imports a Google Font.  
  - JS is vanilla and used for small interactions (nav, smooth scroll, etc.).

- **Website Preview Engine**  
  - Embeds the generated HTML into Streamlit using `st.components.v1.html`.
  - `sanitize_html_for_preview`:
    - Forces all `<a>` tags to open in a new tab.  
    - Wraps the site in a light‑theme `<style>` so text is clearly visible over a white background.

- **ZIP Exporter**  
  - Uses Python’s `zipfile` and `io.BytesIO` to bundle:
    - `index.html`  
    - `style.css`  
    - `script.js`  
  - Streams the ZIP to the user with `st.download_button`.

## Tech Stack

| Layer              | Tool / Library                                          |
|--------------------|-------------------------------------------------------- |
| UI                 | Streamlit                                               |
| Document parsing   | PyPDF2, python‑docx                                     |
| LLM interaction    | Google Gemini via LangChain (`ChatGoogleGenerativeAI`)  |
| Language           | Python                                                  |
| Packaging          | `zipfile`, `io.BytesIO`                                 |
| Preview            | Streamlit HTML component                                |

## How It Works (Step‑By‑Step)

1. **User uploads resume**  
   - Streamlit `file_uploader` accepts `.pdf` or `.docx` files.

2. **Text extraction**  
   - If PDF: `PdfReader` iterates pages and concatenates text.
   - If DOCX: `Document` reads all paragraphs and joins them.

3. **LLM #1: Build website specification**  
   - The resume text is sent to Gemini with a prompt instructing it to act as a career coach and portfolio strategist.
   - The model returns a structured but **non‑code** spec describing sections, content, and design hints.

4. **User review / edit spec (optional)**  
   - Specification is shown in a `st.text_area`.  
   - User can tweak wording, section titles, or style instructions before generating the website.

5. **LLM #2: Generate website code**  
   - The edited spec is sent to Gemini with a frontend‑engineer system prompt.  
   - Response is parsed using the `--html-- / --css-- / --js--` markers into three strings.

6. **Preview in Streamlit**  
   - Code is passed through `sanitize_html_for_preview`:
     - Adds `target="_blank"` to all links.  
     - Injects CSS to enforce a light background and dark text.  
   - Rendered inside the app using `st.components.v1.html` with scrollable height.

7. **Download website ZIP**  
   - `create_zip_bytes` writes the three files into an in‑memory ZIP.  
   - `st.download_button` lets the user download `portfolio_website.zip` to deploy anywhere.

## Setup and Installation

1. **Clone this repository**

```bash
git clone https://github.com/your-username/ai-portfolio-from-resume.git
cd ai-portfolio-from-resume
```

2. **Create and activate a virtual environment (optional but recommended)**

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

Core packages include Streamlit, PyPDF2, python‑docx, langchain‑google‑genai, and python‑dotenv.

4. **Set up environment variables**

Create a `.env` file in the project root:

```env
gemini=YOUR_GOOGLE_API_KEY
```

`main.py` reads this value and sets `GOOGLE_API_KEY` for the Gemini client.

5. **Run the app**

```bash
streamlit run main.py
```

Then open the local URL (typically `http://localhost:8501`) in your browser.

## Usage

- Click **“Upload Resume”** and select a PDF or DOCX.  
- Click **“Generate Website Specification”** to create a structured summary of your portfolio.  
- Review/edit the specification if needed.  
- Click **“Generate Portfolio Website”** to generate HTML, CSS, and JS.  
- Scroll through the **“Website Preview”** section to view the generated site.  
- Click **“Download Website ZIP”** to get `index.html`, `style.css`, and `script.js` for deployment.

## Possible Improvements

- Multiple visual themes (classic, minimal, dark, gradient).  
- Better resume parsing using NER and section detection.  
- Profile photo upload and automatic image placement.
- Predefined animation/transition templates.  
- One‑click deployment to GitHub Pages, Netlify, or Vercel.

## Demo video of execution and result:

https://github.com/user-attachments/assets/6c538c9f-3f9b-4b2a-a697-589752c5a4c8


# Author

Email: pruchita565@gmail.com

Twitter: [ruchita_patil15](https://x.com/ruchita_patil15)

LinkedIn: www.linkedin.com/in/patil-ruchita

