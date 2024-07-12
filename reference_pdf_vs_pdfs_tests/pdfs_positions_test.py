import fitz
import glob
import pytest
from typing import NamedTuple
from .related_files.path import get_path
from .related_files.pdf_reader import pdf_reader


class Cases(NamedTuple):
    reference_pdf: dict
    reference_positions: dict
    test_pdf: dict
    test_positions: dict
    test_pdf_path: str


def get_cases():
    reference_pdf = pdf_reader(get_path('reference_pdf'))
    reference_positions = extract_field_positions(get_path('reference_pdf'), reference_pdf)
    test_pdf_paths = glob.glob(get_path('generated_pdfs')+"*.pdf")
    if not test_pdf_paths:
        raise ValueError("No PDF files found in the specified path")
    for test_pdf_path in test_pdf_paths:
        test_pdf = pdf_reader(test_pdf_path)
        test_positions = extract_field_positions(test_pdf_path, test_pdf)
        yield Cases(reference_pdf, reference_positions, test_pdf, test_positions, test_pdf_path)


def normalize_text(text):
    return text.strip().replace(" ", "").lower()


def extract_field_positions(pdf_path, fields):
    doc = fitz.open(pdf_path)
    page = doc[0]
    text_instances = page.get_text("dict")["blocks"]
    positions = {}

    normalized_fields = {normalize_text(key): key for key in fields}

    for block in text_instances:
        if block["type"] == 0:  # block contains text
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if ':' in text:
                        text = text.split(':')[0].strip()
                    normalized_text = normalize_text(text)
                    if normalized_text in normalized_fields:
                        positions[normalized_fields[normalized_text]] = span["bbox"]
                    print(f"Extracted text: {text}, normalized: {normalized_text}, bbox: {span['bbox']}")

    return positions


def compare_positions(reference_positions, test_positions) -> list:
    results = []

    for k, expected in reference_positions.items():
        actual = test_positions.get(k)
        if actual is not None:
            if expected != actual:
                results.append(
                    f"Position of {k} differs: Actual {actual} not equal to Expected {expected}"
                )
            del test_positions[k]
        else:
            results.append(f"Missing position for key in test PDF: {k}")
    if test_positions:
        extra_keys = ", ".join(test_positions.keys())
        results.append(f"Extra positions in test PDF: {extra_keys}")

    return results


@pytest.mark.parametrize("case", get_cases())
def test_pdf_check(case):
    if not isinstance(case, Cases):
        raise case

    reference_pdf, reference_positions, test_pdf, test_positions, test_pdf_path = case

    position_differences = compare_positions(reference_positions, test_positions)

    if position_differences:
        diff_text = ",\n".join(position_differences)
        pytest.fail(f"{test_pdf_path} failed. Differences:\n{diff_text}")

# For debugging purposes
if __name__ == "__main__":
    for case in get_cases():
        reference_pdf, reference_positions, test_pdf, test_positions, test_pdf_path = case
        print(f"reference_pdf = {reference_pdf}")
        print(f"reference_positions = {reference_positions}")
        print(f"test_pdf = {test_pdf}")
        print(f"test_positions = {test_positions}")
        position_differences = compare_positions(reference_positions, test_positions)
        if position_differences:
            diff_text = ",\n".join(position_differences)
            print(f"{test_pdf_path} failed. Differences:\n{diff_text}")
