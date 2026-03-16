"""
Outputs the table to cvs.
"""

import csv
import logging
import os

log = logging.getLogger(__name__)


def write_to_csv(table, file_path):
    """
    Writes a numpy array table to a .csv file.
    Overrides existing files.

    :param table: Array of table data
    :type table: ndarray
    :param file_path: Output location
    :type file_path: str
    """
    if os.path.exists(file_path):
        log.info(f"File: {file_path} overwritten.")
    with open(file_path, "w", encoding="utf-8") as f:
        csv.writer(f).writerows(table)
