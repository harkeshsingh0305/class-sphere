import pymupdf


def extract_text(pdf_path):
    doc = pymupdf.open(pdf_path)

    # Stop if the PDF has a password
    if doc.needs_pass:
        doc.close()
        raise ValueError("PDF is password protected")

    pages_text = []

    for page in doc:
        text = page.get_text()
        pages_text.append(text)

    doc.close()

    # Join all pages and remove extra blank space
    return "\n".join(pages_text).strip()