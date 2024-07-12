import glob
import pytest
from typing import NamedTuple
from .related_files.path import get_path
from .related_files.pdf_reader import pdf_reader


class Cases(NamedTuple):
    reference_pdf: dict
    test_pdf: dict
    test_pdf_path: str


def get_cases() -> Cases | ValueError:
    """
    Preparing test data.
    Reading the reference file and reading files for check and return them to the test.
    :return: an object of the Cases class
    """
    reference_pdf = pdf_reader(get_path('reference_pdf'))
    test_pdf_paths = glob.glob(get_path('generated_pdfs')+"*.pdf")
    if not test_pdf_paths:
        raise ValueError("No PDF files found in the specified path")
    for test_pdf_path in test_pdf_paths:
        test_pdf = pdf_reader(test_pdf_path)
        yield Cases(reference_pdf, test_pdf, test_pdf_path)


def compare_pdfs(reference_pdf: dict, test_pdf: dict) -> list[str]:
    """
    Takes the key and value from the reference dictionary, looks for the same key in the dictionary for verification.
    If it finds such a key, it compares their values and if they are not equal,
    then it adds an error to the “result” list and removes this key from the dictionary for checking.
    If it doesn’t find it, it adds an error to the “result” list.
    At the end, it checks that there are no unchecked fields left. If there are any, adds an error to the list.

    :param reference_pdf:
    :param test_pdf:
    :return: list of errors
    """
    results = []
    for k, expected in reference_pdf.items():
        actual = test_pdf.get(k)
        if actual is not None:
            if expected != actual:
                results.append(
                    f"Actual {k} = {actual} not equal to Expected {k} = {expected}"
                )
            del test_pdf[k]
        else:
            results.append(f"Missing key in test PDF: {k}")
    if test_pdf:
        extra_keys = ", ".join(test_pdf.keys())
        results.append(f"Extra keys in test PDF: {extra_keys}")

    return results


@pytest.mark.parametrize("case", get_cases())
def test_pdf_check(case):
    """
    The test compares dictionaries obtained from PDF files with a dictionary from a PDF reference.
    """

    if not isinstance(case, Cases):
        raise case

    reference_pdf, test_pdf, test_pdf_path = case
    differences = compare_pdfs(reference_pdf, test_pdf)

    if differences:
        diff_text = ",\n".join(differences)
        pytest.fail(f"{test_pdf_path} failed. Differences:\n{diff_text}")
