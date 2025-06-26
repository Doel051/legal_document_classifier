from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_pdf(file_storage):
    reader = PdfReader(file_storage)
    text = ''
    for page in reader.pages:
        text += page.extract_text() or ''
    return text

def extract_text_from_docx(file_storage):
    file_storage.seek(0)  # Reset pointer
    document = Document(file_storage)
    return '\n'.join([para.text for para in document.paragraphs])

def extract_text_from_txt(file_storage):
    file_storage.seek(0)  # Reset pointer
    return file_storage.read().decode('utf-8')
