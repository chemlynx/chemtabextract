"""
Reads a `csv` formatted table from file. The file has to be 'utf-8' encoded.
"""

import csv
import logging

import numpy as np

log = logging.getLogger(__name__)

_TRUNCATION_WARNING_THRESHOLD = 200


def read(file_path):
    """
    :param file_path: Path to `.csv` input file
    :type file_path: str
    :return: numpy.ndarray
    """

    with open(file_path, encoding="utf-8") as f:
        rows = [elem for elem in list(csv.reader(f)) if elem]
        n = len(rows[0])
        rows = [x for x in rows if len(x) == n]  # Only include rows with data for every column

    # Derive dtype width from actual cell content to avoid silent truncation.
    max_len = max((len(cell) for row in rows for cell in row), default=1)
    if max_len > _TRUNCATION_WARNING_THRESHOLD:
        log.warning(
            f"CSV input contains cells up to {max_len} characters wide. "
            "Values exceeding this length will be stored in full but may indicate "
            "unexpected data (e.g. embedded HTML or very long IUPAC names)."
        )
    array = np.asarray(rows, dtype=f"<U{max(max_len, 1)}")
    return array
