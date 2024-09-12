import io
import os
from typing import IO, Any
import csv

import chardet
import docx
import openpyxl
import pptx
from pypdf import PdfReader
from pypdf.errors import PdfStreamError

TEXT_SECTION_SEPARATOR = "\n\n"

VALID_FILE_EXTENSIONS = [
    ".txt", ".md", ".pdf", ".docx", ".pptx", ".xlsx", ".csv"
]

# ... (keep other functions unchanged)

def csv_to_text(file: IO[Any]) -> str:
    csv_content = file.read().decode('utf-8')
    csv_reader = csv.reader(io.StringIO(csv_content))
    return "\n".join([", ".join(row) for row in csv_reader])

def extract_file_text(file_name: str, file: IO[Any]) -> str:
    extension = get_file_ext(file_name)
    if not check_file_ext_is_valid(extension):
        raise ValueError(f"Unsupported file extension: {extension}")

    if extension in ['.txt', '.md']:
        return read_text_file(file)
    elif extension == '.pdf':
        return pdf_to_text(file)
    elif extension == '.docx':
        return docx_to_text(file)
    elif extension == '.pptx':
        return pptx_to_text(file)
    elif extension in ['.xlsx', '.csv']:
        return csv_to_text(file)
    else:
        raise ValueError(f"Unsupported file extension: {extension}")