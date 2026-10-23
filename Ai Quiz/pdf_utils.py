# pdf_utils.py

def extract_text_from_pdf(file_bytes):
    import fitz  # this is pymupdf

    text_parts = []
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
        for page in pdf:
            text_parts.append(page.get_text())
    return "\n".join(text_parts).strip()