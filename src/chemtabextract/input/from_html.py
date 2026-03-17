"""
Reads an `html` formatted table.
"""

import copy
import logging
from itertools import product

import numpy as np
import requests
from bs4 import BeautifulSoup, Tag

from chemtabextract.exceptions import InputError

_TRUNCATION_WARNING_THRESHOLD = 200

try:
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options as FirefoxOptions

    _SELENIUM_AVAILABLE = True
except ImportError:
    _SELENIUM_AVAILABLE = False

log = logging.getLogger(__name__)


def makearray(html_table: Tag) -> np.ndarray:
    """
    Creates a numpy array from an `.html` file, taking `rowspan` and `colspan` into account.

    Modified from:
        John Ricco, https://johnricco.github.io/2017/04/04/python-html/, *Using Python to scrape HTML tables with merged cells*

    Added functionality for duplicating cell content for cells with `rowspan`/`colspan`.
    The table has to be :math:`n*m`, rectangular, with the same number of columns in every row.
    """
    n_cols = 0
    n_rows = 0

    for row in html_table.findAll("tr"):
        col_tags = row.find_all(["td", "th"])
        if len(col_tags) > 0:
            n_rows += 1
            row_logical_width = sum(int(tag.get("colspan", 1)) for tag in col_tags)
            if row_logical_width > n_cols:
                n_cols = row_logical_width

    # Use object dtype as a build buffer so no cell text is truncated during
    # iteration.  The array is cast to a narrow Unicode dtype at the end.
    array = np.full((n_rows, n_cols), fill_value="", dtype=object)

    # list to store rowspan values
    skip_index = [0 for i in range(0, n_cols)]

    # iterating over each row in the table
    row_counter = 0
    for row in html_table.findAll("tr"):
        # skip row if it's empty
        if len(row.find_all(["td", "th"])) == 0:
            continue

        else:
            # get all the cells containing data in this row
            columns = row.find_all(["td", "th"])
            col_dim = []
            row_dim = []
            col_dim_counter = -1
            row_dim_counter = -1
            col_counter = -1
            this_skip_index = copy.deepcopy(skip_index)

            for col in columns:
                # determine all cell dimensions
                colspan = col.get("colspan")
                if not colspan:
                    col_dim.append(1)
                else:
                    col_dim.append(int(colspan))
                col_dim_counter += 1

                rowspan = col.get("rowspan")
                if not rowspan:
                    row_dim.append(1)
                else:
                    row_dim.append(int(rowspan))
                row_dim_counter += 1

                # adjust column counter
                if col_counter == -1:
                    col_counter = 0
                else:
                    col_counter = col_counter + col_dim[col_dim_counter - 1]

                while skip_index[col_counter] > 0:
                    col_counter += 1

                # get cell contents
                cell_data = col.get_text()

                # insert data into cell
                array[row_counter, col_counter] = cell_data

                # Insert data into neighbouring rowspan/colspan cells
                if colspan:
                    for spanned_col in range(col_counter + 1, col_counter + int(colspan)):
                        array[row_counter, spanned_col] = cell_data
                if rowspan:
                    for spanned_row in range(row_counter + 1, row_counter + int(rowspan)):
                        array[spanned_row, col_counter] = cell_data
                # Fill intersection (corner) cells when both rowspan and colspan are set
                if rowspan and colspan:
                    for r, c in product(range(1, int(rowspan)), range(1, int(colspan))):
                        array[row_counter + r, col_counter + c] = cell_data

                # record column skipping index for every column spanned by this cell
                if row_dim[row_dim_counter] > 1:
                    for spanned_c in range(col_counter, col_counter + col_dim[col_dim_counter]):
                        this_skip_index[spanned_c] = row_dim[row_dim_counter]

        # adjust row counter
        row_counter += 1

        # adjust column skipping index
        skip_index = [i - 1 if i > 0 else i for i in this_skip_index]

    # Derive dtype width from actual cell content to avoid silent truncation.
    max_len = max((len(str(cell)) for cell in array.flat), default=1)
    if max_len > _TRUNCATION_WARNING_THRESHOLD:
        log.warning(
            f"HTML input contains cells up to {max_len} characters wide. "
            "Values exceeding this length will be stored in full but may indicate "
            "unexpected data (e.g. embedded HTML or very long IUPAC names)."
        )
    return array.astype(f"<U{max(max_len, 1)}")


def read_file(file_path: str, table_number: int = 1) -> np.ndarray:
    """Read an HTML file and return the specified table as a numpy array.

    Args:
        file_path: Path to the ``.html`` file.
        table_number: 1-based index of the table to read.  The first table on
            the page is ``1`` (the default).

    Returns:
        The table as a numpy array of Unicode strings.

    Raises:
        InputError: When *table_number* exceeds the number of tables in the file.
    """
    with open(file_path, encoding="UTF-8") as file:
        html_soup = BeautifulSoup(file, features="lxml")
    try:
        html_table = html_soup.find_all("table")[table_number - 1]
    except IndexError:
        raise InputError(f"table_number={table_number} is out of range")
    array = makearray(html_table)
    return array


def configure_selenium(browser="Firefox", geckodriver_path=None):
    """
    Configuration for `Selenium <https://selenium-python.readthedocs.io/>`_.

    :param browser: Which browser to use
    :type browser: str
    :param geckodriver_path: Absolute path to the ``geckodriver`` executable.
        If ``None``, geckodriver must be discoverable on the system ``PATH``
        (Selenium ≥ 4 handles this automatically).
    :type geckodriver_path: str | None
    :return: Selenium driver

    """
    if browser == "Firefox":
        options = FirefoxOptions()
        options.add_argument("--headless")
        if geckodriver_path is not None:
            from selenium.webdriver.firefox.service import Service as FirefoxService

            driver = webdriver.Firefox(
                options=options, service=FirefoxService(executable_path=geckodriver_path)
            )
        else:
            driver = webdriver.Firefox(options=options)
        return driver
    return None


def read_url(url: str, table_number: int = 1) -> np.ndarray:
    """Fetch a table from a URL and return it as a numpy array.

    Tries the ``requests`` library first; falls back to Selenium if the initial
    request fails (requires the ``[web]`` optional extra).

    Args:
        url: URL of the page containing the table.
        table_number: 1-based index of the table on the page (default ``1``).

    Returns:
        The table as a numpy array of Unicode strings.

    Raises:
        TypeError: When *table_number* is not an integer.
        InputError: When *table_number* is out of range, or when ``requests``
            fails and Selenium is not installed.
    """

    if not isinstance(table_number, int):
        msg = "Table number is not valid."
        log.critical(msg)
        raise TypeError(msg)

    # first try the requests package, if it fails do the selenium, which is much slower
    try:
        html_file = requests.get(url)
        html_soup = BeautifulSoup(html_file.text, features="lxml")
        try:
            html_table = html_soup.find_all("table")[table_number - 1]
        except IndexError:
            raise InputError(f"table_number={table_number} is out of range")
        array = makearray(html_table)
        log.info("Package 'requests' was used.")
        return array
    except InputError:
        raise
    except requests.exceptions.RequestException as exc:
        log.warning(f"requests failed ({exc}); attempting Selenium fallback")
        if not _SELENIUM_AVAILABLE:
            raise InputError(
                "requests failed to fetch the URL and selenium is not installed. "
                "Install the optional web extra to enable JS-rendered URL support: "
                "uv add chemtabextract[web]"
            ) from exc
        driver = configure_selenium()
        driver.get(url)
        html_file = driver.page_source
        html_soup = BeautifulSoup(html_file, features="lxml")
        try:
            html_table = html_soup.find_all("table")[table_number - 1]
        except IndexError:
            raise InputError(f"table_number={table_number} is out of range")
        else:
            array = makearray(html_table)
            log.info("Package 'selenium' was used.")
            return array
