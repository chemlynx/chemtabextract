"""
Category table and row-header helpers for chemtabextract.
Internal sub-module — do not import directly from outside algorithms/.
"""

import logging

import numpy as np
from sympy import Symbol, factor_list

log = logging.getLogger(__name__)


def categorize_header(header):
    """
    Performs header categorization (calls the `SymPy` `fact` function) for a given table.

    :param header: header region, Numpy array
    :return: factor_list
    """

    # empty expression and part of the expression that will be factorized
    # these are SymPy expressions
    expression = 0
    part = 0
    for row_index, row in enumerate(header):
        for column_index, cell in enumerate(row):
            if column_index == 0:
                part = Symbol(cell)
            else:
                part = part * Symbol(cell)
        expression = expression + part
    # factorization
    # f = factor(expression, deep=True)
    f = factor_list(expression)
    log.debug(f"Factorization, initial header: {expression}")
    log.debug(f"Factorization, factorized header: {f}")
    return f


def split_table(table_object):
    """
    Splits table into subtables. Yields :class:`~tabledataextractor.table.table.Table` objects.

    Algorithm:
        If the stub header is repeated in the column header section the table is split up before
        the repeated element.

    :param table_object: Input Table object
    :type table_object: ~tabledataextractor.table.table.Table
    """

    # first, the column header
    i = 0
    # the last row of the column/stub header is not used, as it will be determined as
    # data region by the main MIPS algorithm
    for col_index, column in enumerate(table_object.col_header[:-1].T):
        # the first match is backwards and forwards looking
        if (
            i == 0
            and column.size > 0
            and table_object.stub_header[:-1].T[0].size > 0
            and np.array_equal(column, table_object.stub_header[:-1].T[0])
        ):
            yield table_object._pre_cleaned_table[:, 0 : col_index + 1].tolist()
            i += 1
        # every other match is only forwards looking
        if (
            i > 0
            and column.size > 0
            and table_object.stub_header[:-1].T[0].size > 0
            and np.array_equal(column, table_object.stub_header[:-1].T[0])
        ):
            yield table_object._pre_cleaned_table[
                :, col_index + 1 : col_index + i * col_index + 2
            ].tolist()
            i += 1

    # now the same thing for the row header
    i = 0
    for row_index, row in enumerate(table_object.row_header[:, :-1]):
        # the first match is backwards and forwards looking
        if (
            i == 0
            and row.size > 0
            and table_object.stub_header[0, :-1].size > 0
            and np.array_equal(row, table_object.stub_header[0, :-1])
        ):
            yield table_object._pre_cleaned_table[0 : row_index + 1, :].tolist()
            i += 1
        # every other match is only forwards looking
        if (
            i > 0
            and row.size > 0
            and table_object.stub_header[0, :-1].size > 0
            and np.array_equal(row, table_object.stub_header[0, :-1])
        ):
            yield table_object._pre_cleaned_table[
                row_index + 1 : row_index + i * row_index + 2, :
            ].tolist()
            i += 1


def find_row_header_table(category_table, stub_header):
    """
    Constructs a Table from the row categories of the original table.

    :param category_table: ~tabledataextractor.table.table.Table.category_table
    :type category_table: list
    :param stub_header: ~tabledataextractor.table.table.Table.stub_header
    :type stub_header: numpy.ndarray
    :return: list
    """
    stub_header = stub_header.tolist()
    raw_table = list()
    for line in stub_header:
        new_line = list()
        for item in line:
            new_line.append(item)
        raw_table.append(new_line)
    for line in category_table:
        new_line = list()
        for item in line[1]:
            new_line.append(item)
        raw_table.append(new_line)
    return raw_table


def clean_row_header(pre_cleaned_table, cc2):
    """
    Cleans the row header by removing duplicate rows that span the whole table.
    """
    unmodified_part = pre_cleaned_table[: cc2[0] + 1, :]
    modified_part = pre_cleaned_table[cc2[0] + 1 :, :]

    # delete duplicate rows that extend over the whole table
    _, indices = np.unique(modified_part, axis=0, return_index=True)
    # for logging only, which rows have been removed
    removed_rows = []
    for row_index in range(0, len(modified_part)):
        if row_index not in indices:
            removed_rows.append(row_index)
    # deletion
    modified_part = modified_part[np.sort(indices)]

    return np.vstack((unmodified_part, modified_part))
