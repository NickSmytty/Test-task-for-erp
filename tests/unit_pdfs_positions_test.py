"""Contains test to check common test"""

from pathlib import Path
from typing import Any

pytest_plugins = "pytester"


def test_compare_pdfs_positions(
    pytester: Any, request: Any,
) -> None:
    """Run common tests and check result."""
    path = Path(
        f"{request.config.rootdir}/reference_pdf_vs_pdfs_tests/pdfs_positions_test.py"
    )
    test_result = pytester.runpytest_subprocess(path, "--tb=auto", "-vv")
    # Check number of passed skipped tests.
    # if number of failed is not passed to assert_outcomes,
    # it means failed=0, it is applicable for other test statuses.
    test_result.assert_outcomes(failed=10, passed=1)
