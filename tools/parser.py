import os
import pdfplumber
import docx2txt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def resolve_path(file_path: str) -> str:
    """Resolve file path relative to current working directory or project root."""
    if os.path.isabs(file_path) and os.path.exists(file_path):
        return file_path
    if os.path.exists(file_path):
        return os.path.abspath(file_path)
    relative_to_base = os.path.join(BASE_DIR, file_path)
    if os.path.exists(relative_to_base):
        return relative_to_base
    return file_path

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF resume."""
    pdf_path = resolve_path(pdf_path)
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(docx_path: str) -> str:
    """Extract text from a DOCX resume."""
    docx_path = resolve_path(docx_path)
    return docx2txt.process(docx_path)

def read_text_from_file(file_path: str) -> str:
    """Read text from a file."""
    file_path = resolve_path(file_path)
    with open(file_path, "r", encoding="utf-8", errors="replace") as file:
        return file.read()

if __name__ == "__main__":
    print(extract_text_from_pdf("resumes/test.pdf"))
    print(extract_text_from_docx("resumes/test.docx"))
