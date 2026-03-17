"""
Analyzes the input and calls the appropriate input module.
"""

import logging
from pathlib import Path
from urllib.parse import urlparse

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


def html(name):
    """
    Returns `True` if input is `html` file.

    :param name: Input string
    :type name: str
    """
    if Path(name).is_file() and name.endswith(".html"):
        return True
    else:
        return False


def csv(name):
    """
    Returns `True` if input is `csv` file.

    :param name: Input string
    :type name: str
    """
    if Path(name).is_file() and name.endswith(".csv"):
        return True
    else:
        return False


def create_table(name_key, table_number=1):
    """
    Checks the input and calls the appropriate modules for conversion.
    Returns a numpy array with the raw table.

    :param name_key: Path to `.html` or `.cvs` file, `URL` or `python list` that is used as input
    :type name_key: str | list
    :param table_number: Number of the table that we want to input if there are several at the given address/path
    :type table_number: int
    :return: table as numpy.array
    """

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
            raise TypeError(msg, str(name_key))

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
        raise TypeError(msg, str(name_key))
