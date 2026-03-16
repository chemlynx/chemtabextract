"""
Array utility helpers for chemtabextract.
Internal sub-module — do not import directly from outside algorithms/.
"""

import logging

import numpy as np

from chemtabextract.table.parse import CellParser, StringParser

log = logging.getLogger(__name__)


def empty_string(string, regex=r"^([\s\-\–\—\"]+)?$"):
    """
    Returns `True` if a particular string is empty, which is defined with a regular expression.

    :param string: Input string for testing
    :type string: str
    :param regex: The regular expression which defines an empty cell (can be tweaked).
    :type regex: str
    :return: True/False
    """
    empty_parser = StringParser(regex)
    return empty_parser.parse(string, method="fullmatch")


def empty_cells(array, regex=r"^([\s\-\–\—\"]+)?$"):
    """
    Returns a mask with `True` for all empty cells in the original array and `False` for non-empty cells.

    :param regex: The regular expression which defines an empty cell (can be tweaked).
    :type regex: str
    :param array: Input array to return the mask for
    :type array: numpy array
    """
    empty = np.full_like(array, fill_value=False, dtype=bool)
    empty_parser = CellParser(regex)
    for empty_cell in empty_parser.parse(array, method="fullmatch"):
        if array.ndim == 2:
            empty[empty_cell[0], empty_cell[1]] = True
        elif array.ndim == 1:
            empty[empty_cell[0]] = True
    return empty


def standardize_empty(array):
    """
    Returns an array with the empty cells of the input array standardized to 'NoValue'.

    :param array: Input array
    :type array: numpy.array
    :return: Array with standardized empty cells
    """
    standardized = np.copy(array)
    for row_index, row in enumerate(standardized):
        for col_index, col in enumerate(row):
            if empty_string(col):
                standardized[row_index, col_index] = "NoValue"
    return standardized


def pre_clean(array):
    """
    Removes empty and duplicate rows and columns that extend over the whole table.

    :param array: Input Table object
    :type array: Numpy array
    """

    pre_cleaned_table = np.copy(array)
    array_empty = empty_cells(array)

    # find empty rows and delete them
    empty_rows = []
    for row_index, row in enumerate(array_empty):
        if False not in row:
            empty_rows.append(row_index)
    log.debug(f"Empty rows {empty_rows} deleted.")
    pre_cleaned_table = np.delete(pre_cleaned_table, empty_rows, axis=0)

    # find empty columns and delete them
    empty_columns = []
    for column_index, column in enumerate(array_empty.T):
        if False not in column:
            empty_columns.append(column_index)
    log.debug(f"Empty columns {empty_columns} deleted.")
    pre_cleaned_table = np.delete(pre_cleaned_table, empty_columns, axis=1)

    # delete duplicate rows that extend over the whole table
    _, indices = np.unique(pre_cleaned_table, axis=0, return_index=True)
    # for logging only, which rows have been removed
    removed_rows = []
    for row_index in range(0, len(pre_cleaned_table)):
        if row_index not in indices:
            removed_rows.append(row_index)
    log.debug(f"Duplicate rows {removed_rows} removed.")
    # deletion:
    pre_cleaned_table = pre_cleaned_table[np.sort(indices)]

    # delete duplicate columns that extend over the whole table
    _, indices = np.unique(pre_cleaned_table, axis=1, return_index=True)
    # for logging only, which rows have been removed
    removed_columns = []
    for column_index in range(0, len(pre_cleaned_table.T)):
        if column_index not in indices:
            removed_columns.append(column_index)
    log.debug(f"Duplicate columns {removed_columns} removed.")
    # deletion:
    pre_cleaned_table = pre_cleaned_table[:, np.sort(indices)]

    # clean-up unicode characters
    pre_cleaned_table = clean_unicode(pre_cleaned_table)

    return pre_cleaned_table


def clean_unicode(array):
    """
    Replaces problematic unicode characters in a given numpy array.
    :param array: input array
    :type array: numpy.array
    :return: cleaned array
    """
    temp = np.copy(array)
    temp = np.char.replace(temp, "\xa0", " ")
    return temp


def duplicate_rows(table):
    """
    Returns True if there are duplicate rows in the table and False if there are no duplicate rows
    :param table:
    :return: True or False
    """
    if table.ndim > 0 and table.size:
        _, indices = np.unique(table, axis=0, return_index=True)
        if len(table) > len(indices):
            return True
        else:
            return False
    else:
        return False


def duplicate_columns(table):
    """
    Returns True if there are duplicate columns in the table and False if there are no duplicate columns
    :param table:
    :return: True or False
    """
    if table.T.ndim > 0 and table.T.size:
        _, indices = np.unique(table.T, axis=0, return_index=True)
        if len(table.T) > len(indices):
            return True
        else:
            return False
    else:
        return False
