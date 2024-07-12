import fitz
import os


def pdf_reader(pdf_path: str = None) -> dict:
    """
    Read PDF file and return dict with values from this file
    :param pdf_path: path to PDF file
    :return: dict with values
    """
    if pdf_path is None:
        raise ValueError("The path to the PDF file must be specified.")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()

    info_dict = {}
    lines = text.split("\n")
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            info_dict[key.strip()] = value.strip()

    return info_dict