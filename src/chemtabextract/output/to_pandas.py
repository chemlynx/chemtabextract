"""
Outputs the table to a Pandas DataFrame.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from chemtabextract.table.table import Table


def to_pandas(table: Table) -> pd.DataFrame:
    """
    Creates a `Pandas <http://pandas.pydata.org/>`_ `DataFrame` object from a :class:`~chemtabextract.table.table.Table` object.

    :param table: Input table
    :type table: ~chemtabextract.table.table.Table
    :return: :class:`pandas.DataFrame`
    """
    index_row = pd.MultiIndex.from_arrays(table.row_header.T)
    index_col = pd.MultiIndex.from_arrays(table.col_header)
    df = pd.DataFrame(columns=index_col, index=index_row, data=table.data)
    return df


def find_multiindex_level(
    row_number: int, column_number: int, df: pd.DataFrame
) -> tuple[list, list]:
    """
    Helper for :func:`build_category_table` and :func:`print_category_table`.

    Finds the `Pandas` `MultiIndex level` in a given `Pandas` `DataFrame`,
    for a particular data value identified by row/column index.

    :param row_number: Row index into the DataFrame values array.
    :type row_number: int
    :param column_number: Column index into the DataFrame values array.
    :type column_number: int
    :param df: Pandas DataFrame with MultiIndex rows and columns.
    :type df: pandas.DataFrame
    :return: Tuple of (row_categories, column_categories) lists.
    :rtype: tuple[list, list]
    """
    result_index = []
    if hasattr(df.index, "codes"):
        for i, codes in enumerate(df.index.codes):
            result_index.append(df.index.levels[i][codes[row_number]])
    else:
        result_index.append(df.index[row_number])
    result_column = []
    if hasattr(df.columns, "codes"):
        for i, codes in enumerate(df.columns.codes):
            result_column.append(df.columns.levels[i][codes[column_number]])
    else:
        result_column.append(df.columns[column_number])
    return result_index, result_column


def print_category_table(df: pd.DataFrame) -> None:
    """
    Prints the category table to screen, from `Pandas DataFrame` input

    :param df: Pandas DataFrame input
    :type df: pandas.DataFrame
    """
    values = df.values  # data is converted to numpy array
    print(
        "{:11s} {:10s} {:36s} {:20s}".format(
            "Cell_ID", "Data", "Row Categories", "Column Categories"
        )
    )
    for i, row in enumerate(values):
        for j, cell in enumerate(row):
            categories = find_multiindex_level(i, j, df)
            print(
                "{:3} {:3} {:15}   {:35}  {:40}".format(
                    i, j, str(cell), "".join(str(categories[0])), "".join(str(categories[1]))
                )
            )


def build_category_table(df: pd.DataFrame) -> list:
    """
    Builds the category table in form of a Python list, from `Pandas DataFrame` input

    :param df: Pandas DataFrame input
    :type df: pandas.DataFrame
    :return: category_table as Python list
    """
    values = df.values  # data is converted to numpy array
    category_table = []
    for i, row in enumerate(values):
        for j, cell in enumerate(row):
            data_point = []
            categories = find_multiindex_level(i, j, df)
            data_point.append(cell)
            data_point.append(categories[0])
            data_point.append(categories[1])
            category_table.append(data_point)
    return category_table
