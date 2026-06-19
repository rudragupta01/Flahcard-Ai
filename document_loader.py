import pdfplumber

def load_pdf(file_path):
    """Extract text from a single PDF file"""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text.strip()

def load_multiple_pdfs(file_paths_with_names):
    """
    Extract text from multiple PDFs, tagging each chunk with its source filename.
    file_paths_with_names: list of tuples (file_path, original_filename)
    Returns: list of dicts [{"filename": ..., "text": ...}, ...]
    """
    results = []
    for file_path, filename in file_paths_with_names:
        text = load_pdf(file_path)
        if text:
            results.append({"filename": filename, "text": text})
    return results

def load_text(text_input):
    """Accept plain pasted text directly"""
    return text_input.strip()