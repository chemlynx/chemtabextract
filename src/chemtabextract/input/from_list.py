"""
Inputs from python list object.
"""

import logging

import numpy as np

log = logging.getLogger(__name__)

_TRUNCATION_WARNING_THRESHOLD = 200


def read(plist: list) -> np.ndarray:
    """Create a numpy array from a Python list.

    Rows of different lengths are padded with ``None`` to match the longest row.

    Args:
        plist: Input list of rows; each row is itself a list of cell values.

    Returns:
        The table as a numpy array of Unicode strings with a dtype wide enough
        to hold all cell values without truncation.
    """
    length = len(sorted(plist, key=len, reverse=True)[0])
    padded = [row + [None] * (length - len(row)) for row in plist]

    # Derive dtype width from actual cell content to avoid silent truncation.
    max_len = max((len(str(cell)) for row in padded for cell in row if cell is not None), default=1)
    if max_len > _TRUNCATION_WARNING_THRESHOLD:
        log.warning(
            f"List input contains cells up to {max_len} characters wide. "
            "Values exceeding this length will be stored in full but may indicate "
            "unexpected data (e.g. embedded HTML or very long IUPAC names)."
        )
    array = np.array(padded, dtype=f"<U{max(max_len, 1)}")
    return array
