"""
Header, structure, and spanning-cell helpers for chemtabextract.
Internal sub-module — do not import directly from outside algorithms/.
"""

import logging

import numpy as np

from chemtabextract.exceptions import MIPSError
from chemtabextract.table.algorithms._mips import find_cc1_cc2, find_cc4
from chemtabextract.table.algorithms._utils import (
    duplicate_columns,
    duplicate_rows,
    empty_cells,
    empty_string,
)

log = logging.getLogger(__name__)


def find_title_row(table_object):
    """
    Searches for the topmost non-empty row.

    :param table_object: Input Table object
    :type table_object: ~chemtabextract.table.table.Table
    :return: int
    """
    for row_index, empty_row in enumerate(table_object.pre_cleaned_table_empty):
        if not empty_row.all():
            return row_index


def find_note_cells(table_object, labels_table):
    """
    Searches for all non-empty cells that have not been labelled differently.

    :param table_object: Input Table object
    :type table_object: ~chemtabextract.table.table.Table
    :param labels_table: table that holds all the labels
    :type labels_table: Numpy array
    :return: Tuple
    """
    for row_index, row in enumerate(labels_table):
        for column_index, cell in enumerate(row):
            if cell == "/" and not table_object.pre_cleaned_table_empty[row_index, column_index]:
                yield row_index, column_index


def prefix_duplicate_labels(table_object, array):
    """
    Prefixes duplicate labels in first row or column where this is possible,
    by adding a new row/column containing the preceding (to the left or above) unique labels, if available.

    Nested prefixing is not supported.

    The algorithm is not completely selective and there might be cases where it's application is undesirable.
    However, on standard datasets it significantly improves table-region classification.

    Algorithm for column headers:

    1. Run MIPS, to find the old header region, without prefixing.
    2. For row in table, can *meaningful* prefixing in this row been done?
        * yes --> do prefixing and go to 3, prefixing of only one row is possible; accept prefixing only if prefixed rows/cells are above the end of the header (not in the data region), the prefixed cells can still be above the header
        * no  --> go to 2, next row
    3. run MIPS to get the new header region
    4. accept prefixing only if the prefixing has not made the header region start lower than before and if it hasn't made the header region wider than before

    The algorithm has been modified from Embley et al., *DOI: 10.1007/s10032-016-0259-1*.

    :param table_object: Input Table object
    :type table_object: ~chemtabextract.table.table.Table
    :param array: Table to use as input and to do the prefixing on
    :type array: Numpy array
    :return: Table with added rows/columns with prefixes, or, input table, if no prefixing was done

    """

    def unique(data, row_or_column):
        """
        Returns True if data is unique in the given row/column or False if not unique or not present.

        :param data:
        :param row_or_column:
        :return:
        """
        count = 0
        for cell in row_or_column:
            if cell == data:
                count += 1
        if count == 1:
            return True
        else:
            return False

    def prefixed_row_or_column(table):
        """
        Main algorithm for creating prefixed column/row headers.
        If cell is not unique, it is prefixed with the first unique above (for row header) or to the left
        (for column header).

        Returns the row/column containing the prefixes and the position of the row/column where the new row/column
        has to be inserted into the original table.

        This function is getting ugly and could be rewritten with the use of a nice list of tuples,
        for every row/column in the table, we would have a list of distinct elements with their positions in the row/column

        :param table: input table (will not be changed)
        :return: row_index: where the row/column has to be inserted, new_row: the list of prefixes
        """

        unique_prefix = False
        prefixed = False
        row_index = 0
        new_row = []
        for row_index, row in enumerate(table):
            duplicated_row = []
            new_row = []
            for _, cell in enumerate(row):
                # append if unique or empty cell
                if unique(cell, row) or empty_string(cell):
                    duplicated_row.append(cell)
                    new_row.append("")
                else:
                    # find the first unique cell to the left
                    # don't use the first column and first row
                    # as these will presumably be in the stub header region
                    for prefix in reversed(duplicated_row[1:]):
                        # use the prefix if it is unique and not empty
                        if unique(prefix, row) and not empty_string(prefix):
                            unique_prefix = prefix
                            break
                    # prefix the cell and append it to new row
                    if unique_prefix:
                        duplicated_row.append(unique_prefix + "/" + cell)
                        new_row.append(unique_prefix)
                        prefixed = True
                    # else, if no unique prefix was found, just append the original cell,
                    else:
                        duplicated_row.append(cell)
                        new_row.append("")
            # and continue to the next row (if no prefixing has been performed)
            if prefixed:
                break
        if prefixed:
            return row_index, new_row
        else:
            return None

    # MAIN ALGORITHM
    # 1. first, check the MIPS, to see what header we would have gotten without the prefixing
    # note, cc4 couldn't have changed
    log.debug("Prefixing. Attempt to run main MIPS algorithm.")
    try:
        cc1, cc2 = find_cc1_cc2(table_object, find_cc4(table_object), array)
    except (MIPSError, TypeError):
        log.error("Prefixing was not performed due to failure of MIPS algorithm.")
        return array

    # this flag is used for the return value, if it doesn't change the original table is returned
    prefixed = False

    # 2. DO THE PREFIXING
    # prefixing of column headers
    if prefixed_row_or_column(array):
        row_index, new_row = prefixed_row_or_column(array)
        # only perform prefixing if not below of header region (above is allowed!)
        # to allow prefixing even below the old header region cannot be right
        if row_index <= cc2[0]:
            log.debug(f"Column header prefixing, row_index= {row_index}")
            log.debug(f"Prefixed row= {new_row}")
            # Prefixing by adding new row:
            prefixed = True
            prefixed_table = np.insert(array, row_index, new_row, axis=0)

    # prefixing of row headers
    if prefixed_row_or_column(array.T):
        column_index, new_column = prefixed_row_or_column(array.T)
        # only perform prefixing if not to the right of header region (to the left is allowed!)
        # to allow prefixing even below the old header region cannot be right
        if column_index <= cc2[1]:
            log.debug(f"Row header prefixing, column_index= {column_index}")
            log.debug(f"Prefixed column= {new_column}")
            # Prefixing by adding a new column:
            prefixed = True
            prefixed_table = np.insert(array, column_index, new_column, axis=1)

    # 3. check the headers again, after prefixing
    # note, cc4 couldn't have changed
    if prefixed:
        # if new headers fail, the prefixing has destroyed the table, which is not a HIT table anymore
        try:
            cc1_new, cc2_new = find_cc1_cc2(table_object, find_cc4(table_object), prefixed_table)
        except (MIPSError, TypeError):
            log.debug("Prefixing was not performed because it destroyed the table")
            return array
        # return prefixed_table only if the prefixing has not made the header to start lower,
        # it can end lower (and this is desired and what we want - not to include the data region into the header),
        # but it cannot start lower, because that would mean that we have removed some of the hierarchy and added
        # hierarchy from the left/above into a column/row
        if cc1_new[0] <= cc1[0] and cc1_new[1] <= cc1[1]:
            # Another condition, the header has to end lower than before, not to include at east one
            # lower row/column that was included before
            if cc2_new[0] <= cc2[0] and cc2_new[1] <= cc2[1]:
                table_object.history.set_prefixing_performed(True)
                log.debug("METHOD. Prefixing was performed.")
                if len(prefixed_table.T) > len(array.T):
                    table_object.history.set_prefixed_rows(True)
                return prefixed_table
            else:
                return array
        else:
            return array
    else:
        return array


def duplicate_spanning_cells(table_object, array):
    """
    Duplicates cell contents into appropriate spanning cells. This is sometimes necessary for `.csv` files where
    information has been lost, or, if the source table is not properly formatted.

    Cells outside the row/column header (such as data cells) will not be duplicated.
    MIPS is run to perform a check for that.

    Algorithm according to Nagy and Seth, 2016, in Procs. ICPR 2016, Cancun, Mexico.

    :param table_object: Input Table object
    :type table_object: ~chemtabextract.table.table.Table
    :param array: Table to use as input
    :type array: Numpy array
    :return: Array with spanning cells copied, if necessary. Alternatively, returns the original table.
    """

    def empty_row(arrayy):
        """Returns 'True' if the whole row is truly empty"""
        for element in arrayy:
            if element:
                return False
        return True

    # running MIPS to find the data region
    log.debug("Spanning cells. Attempt to run MIPS algorithm, to find potential title row.")
    try:
        cc1, cc2 = find_cc1_cc2(
            table_object, find_cc4(table_object), table_object.pre_cleaned_table
        )
    except (MIPSError, TypeError):
        log.error("Spanning cells update was not performed due to failure of MIPS algorithm.")
        return array

    log.debug("Spanning cells. Attempt to run main spanning cell algorithm.")
    temp = array.copy()
    top_fill = None
    left_fill = None
    for c in range(0, len(temp.T)):
        flag = 0
        for r in range(cc1[0], len(temp)):
            if temp[r, c]:
                top_fill = temp[r, c]
                flag = 1
            elif flag == 1:
                temp[r, c] = top_fill
            if len(temp) - 1 > r and empty_row(temp[r + 1]):
                flag = 0
    for r in range(cc1[0], len(temp)):
        flag = 0
        for c in range(len(temp.T)):
            if temp[r, c]:
                if (len(temp) - 1 > r and temp[r + 1, c] != temp[r, c]) or temp[r - 1, c] != temp[
                    r, c
                ]:
                    left_fill = temp[r, c]
                    flag = 1
                else:
                    flag = 0
            elif flag == 1:
                temp[r, c] = left_fill
            if len(temp.T) - 1 > c and empty_row(temp.T[c + 1]):
                flag = 0

    # Finding the header regions to make sure the spanning cells additions are not applied in the data region
    # Then, the main MIPS algorithm has to be run
    temp2 = np.copy(temp)
    diff_row_length = 0
    diff_col_length = 0
    if table_object.configs["use_prefixing"]:
        temp2 = prefix_duplicate_labels(table_object, temp)
        # reset the prefixing flag
        table_object.history.set_prefixing_performed(False)
        table_object.history.set_prefixed_rows(False)
        diff_row_length = len(temp2) - len(temp)
        diff_col_length = len(temp2.T) - len(temp.T)
    log.debug("Spanning cells. Attempt to run main MIPS algorithm.")
    # disable title row temporarily
    old_title_row_setting = table_object.configs["use_title_row"]
    table_object.configs["use_title_row"] = False
    try:
        cc1, cc2 = find_cc1_cc2(table_object, find_cc4(table_object), temp2)
    except (MIPSError, TypeError):
        log.error("Spanning cells update was not performed due to failure of MIPS algorithm.")
        return array
    finally:
        table_object.configs["use_title_row"] = old_title_row_setting

    updated = array.copy()
    # update the original table with values from the updated table if the cells are in the header regions
    # update column header
    for col_header_index in range(cc1[0], cc2[0] + 1 - diff_row_length):
        updated[col_header_index, :] = temp[col_header_index, :]

    # update row header
    for row_header_index in range(cc1[1], cc2[1] + 1 - diff_col_length):
        updated[:, row_header_index] = temp[:, row_header_index]

    # log
    if not np.array_equal(updated, array):
        table_object.history.set_spanning_cells_extended(True)
        log.debug("METHOD. Spanning cells extended.")

    return updated


def header_extension_up(table_object, cc1):
    """
    Extends the header after main MIPS run.

    Algorithm according to Nagy and Seth, 2016, *"Table Headers: An entrance to the data mine"*,
    in Procs. ICPR 2016, Cancun, Mexico.

    :param table_object: Input Table object
    :type table_object: ~chemtabextract.table.table.Table
    :param cc1: `CC1` critical cell
    :return: cc1_new
    """

    cc1_new_row = None
    cc1_new_col = None

    # add row above the identified column header if it does not consist of cells with identical values and if it
    # adds at least one non-blank cell that has a value different from the cell immediately below it
    current_row = table_object.pre_cleaned_table[cc1[0], :]
    for row_index in range(cc1[0] - 1, -1, -1):
        # start after the first column to allow for a title
        if len(np.unique(table_object.pre_cleaned_table[row_index, 1:])) == 1:
            cc1_new_row = row_index + 1
        else:
            for col_index, cell in enumerate(table_object.pre_cleaned_table[row_index, :]):
                # remove the first row from this check to preserve a title,
                # if the title is the only non-empty element of the row
                if (
                    col_index != 0
                    and cell != current_row[col_index]
                    and not table_object.pre_cleaned_table_empty[row_index, col_index]
                ):
                    current_row = table_object.pre_cleaned_table[row_index, :]
                    cc1_new_row = row_index
                    break
    if cc1_new_row is None:
        cc1_new_row = cc1[0]

    # now do the same for the row headers
    current_col = table_object.pre_cleaned_table[:, cc1[1]]
    for col_index in range(cc1[1] - 1, -1, -1):
        if len(np.unique(table_object.pre_cleaned_table[:, col_index])) == 1:
            cc1_new_col = col_index + 1
        else:
            for row_index, cell in enumerate(table_object.pre_cleaned_table[:, col_index]):
                if (
                    cell != current_col[row_index]
                    and not table_object.pre_cleaned_table_empty[row_index, col_index]
                ):
                    current_col = table_object.pre_cleaned_table[:, col_index]
                    cc1_new_col = col_index
                    break
    if cc1_new_col is None:
        cc1_new_col = cc1[1]

    cc1_new = (cc1_new_row, cc1_new_col)

    # log
    if not cc1_new == cc1:
        table_object.history.set_header_extended_up(True)
        log.debug("METHOD. Header extended upwards.")

    return cc1_new


def header_extension_down(table_object, cc1, cc2, cc4):
    """
    Extends the header downwards, if no prefixing was done and if the appropriate stub header is empty.
    For column-header expansion downwards, only the first cell of the stub header has to be empty.
    For row-header expansion to the right, the whole stub header column above has to be empty.

    :param table_object: Input Table object
    :type table_object: ~chemtabextract.table.table.Table
    :param cc2: Critical cell `CC2`
    :type cc2: (int, int)
    :param cc1: Critical cell `CC1`
    :type cc1: (int, int)
    :param cc4: Critical cell `CC4`
    :type cc4: (int, int)
    :return: New `cc2`
    """
    cc2_new = cc2
    extended = False

    # only do downwards header extension if no prefixing was done
    if not table_object.history.prefixing_performed:
        # extend column header downwards, changes cc2 row
        # only the first cell of the stub header has to be empty to accept the move downwards
        row_index = cc2[0]
        while row_index <= cc4[0] and empty_string(
            table_object.pre_cleaned_table[row_index, cc1[1]]
        ):
            row_index += 1
            cc2_new = (row_index - 1, cc2_new[1])
            if cc2_new != cc2:
                extended = True

        if extended:
            table_object.history.set_header_extended_down(True)

        # Check if row header can be shortened now, check duplicate rows accordingly, changes cc2 col
        if extended:
            cc2_new_col = cc2_new[1]
            i = len(table_object.row_header.T)
            while not duplicate_rows(table_object.row_header[:, :i]) and i > 1:
                i -= 1
                if not duplicate_rows(table_object.row_header[:, :i]):
                    cc2_new_col -= 1
            cc2_new = (cc2_new[0], cc2_new_col)
            extended = False

        # extend row header to the right, changes cc2 col
        # this check is more rigorous than above, and all the cells in the stub header have to be empty
        col_index = cc2_new[1]
        while (
            col_index <= cc4[1]
            and empty_cells(table_object.pre_cleaned_table[cc1[0] : cc2[0] + 1, col_index]).all()
        ):
            col_index += 1
            if col_index - 1 != cc2_new[1]:
                extended = True
            cc2_new = (cc2_new[0], col_index - 1)

        if extended:
            # Check if column header can be shortened now, changes cc2 row
            cc2_new_row = cc2_new[0]
            i = len(table_object.col_header)
            while not duplicate_columns(table_object.col_header[:i, :]) and i > 1:
                i -= 1
                if not duplicate_columns(table_object.col_header[:i, :]):
                    cc2_new_row -= 1
            cc2_new = (cc2_new_row, cc2_new[1])

        if extended:
            table_object.history.set_header_extended_down(True)

    return cc2_new
