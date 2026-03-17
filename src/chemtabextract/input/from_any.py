"""
Analyzes the input and calls the appropriate input module.
"""

import logging
from pathlib import Path
from urllib.parse import urlparse

import numpy as np

from chemtabextract.input import from_csv, from_html, from_list

log = logging.getLogger(__name__)


def url(name: str) -> bool:
    """Returns ``True`` if *name* is a valid HTTP, HTTPS, or FTP URL.

    Uses :mod:`urllib.parse` (stdlib). Replaces the former Django
    ``URLValidator`` dependency.

    Args:
        name: Input string to test.

    Returns:
        ``True`` when *name* has a scheme of ``http``, ``https``, or ``ftp``
        **and** a non-empty netloc; ``False`` otherwise.
    """
    try:
        result = urlparse(name)
        return result.scheme in {"http", "https", "ftp"} and bool(result.netloc)
    except ValueError:
        return False


def html(name: str) -> bool:
    """Returns ``True`` if *name* is a path to an existing ``.html`` file.

    Args:
        name: Input string (file path).

    Returns:
        ``True`` when the path exists and ends with ``.html``; ``False`` otherwise.
    """
    if Path(name).is_file() and name.endswith(".html"):
        return True
    else:
        return False


def csv(name: str) -> bool:
    """Returns ``True`` if *name* is a path to an existing ``.csv`` file.

    Args:
        name: Input string (file path).

    Returns:
        ``True`` when the path exists and ends with ``.csv``; ``False`` otherwise.
    """
    if Path(name).is_file() and name.endswith(".csv"):
        return True
    else:
        return False


def create_table(name_key: str | Path | list, table_number: int = 1) -> np.ndarray:
    """Check the input type and dispatch to the appropriate parser.

    Args:
        name_key: Path to an ``.html`` or ``.csv`` file, a URL string, or a
            multidimensional Python list.
        table_number: 1-based index of the table to read when multiple tables
            are present at the source.

    Returns:
        The raw table as a numpy array of Unicode strings.

    Raises:
        TypeError: When *name_key* is not a recognised input type.
    """
    # Normalise pathlib.Path objects so all downstream predicates and
    # urllib.parse.urlparse() receive a plain string.
    if isinstance(name_key, Path):
        name_key = str(name_key)

    if isinstance(name_key, list):
        log.info("Input is list type.")
        if len(name_key) > 0:
            return from_list.read(name_key)
        else:
            msg = (
                "Input is invalid. "
                "Supported are: path to .html or .cvs file, URL or multidimensional python list object"
            )
            log.critical(msg)
            raise TypeError(f"{msg}: {name_key!r}")

    elif url(name_key):
        log.info(f"Url: {name_key}")
        return from_html.read_url(name_key, table_number)

    elif html(name_key):
        log.info(f"HTML File: {name_key}")
        return from_html.read_file(name_key, table_number)

    elif csv(name_key):
        log.info(f"CSV File: {name_key}")
        return from_csv.read(name_key)

    else:
        msg = "Input is invalid. Supported are: path to .html or .cvs file, URL or multidimensional python list object"
        log.critical(msg)
        raise TypeError(f"{msg}: {name_key!r}")
