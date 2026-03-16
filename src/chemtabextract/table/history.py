"""
Indicates to the user which methods have been used on the table.
This should be checked for testing on a sample dataset, to justify the choice of settings for the given domain.

.. codeauthor:: Juraj Mavračić <jm2111@cam.ac.uk>

"""

import logging

log = logging.getLogger(__name__)


class History:
    """
    Stores `True`/`False` for each property, indicating if a method has been used on the particular :class:`~tabledataextractor.table.table.Table` instance.
    """

    def __init__(self):
        self._title_row_removed = False
        self._prefixing_performed = False
        self._prefixed_rows = False
        self._footnotes_copied = False
        self._spanning_cells_extended = False
        self._header_extended_up = False
        self._header_extended_down = False
        self._table_transposed = False
        log.debug("History() object created.")

    @property
    def title_row_removed(self):
        """Indicates whether a title row has been removed from the table."""
        return self._title_row_removed

    @property
    def prefixing_performed(self):
        """Indicates whether prefixing has been performed on the table."""
        return self._prefixing_performed

    @property
    def prefixed_rows(self):
        """Indicates whether prefixing has been performed on the rows (left side)."""
        return self._prefixed_rows

    @property
    def footnotes_copied(self):
        """Indicates whether footnotes have been copied into the table cells."""
        return self._footnotes_copied

    @property
    def spanning_cells_extended(self):
        """
        Indicates whether the content of cells has been duplicated into neighbouring cells,
        in case of cells that are merged cells (spanning cells).
        """
        return self._spanning_cells_extended

    @property
    def header_extended_up(self):
        """Indicates whether the header has been extended upwards, beyond the result obtained by the MIPS
        (*Minimum Indexing Point Search*) algorithm."""
        return self._header_extended_up

    @property
    def header_extended_down(self):
        """Indicates whether the header has been extended downwards, beyond the result obtained by the MIPS
        (*Minimum Indexing Point Search*) algorithm."""
        return self._header_extended_down

    @property
    def table_transposed(self):
        """Indicates whether the table has been transposed."""
        return self._table_transposed

    def __repr__(self):
        out = ""
        out += f"title_row_removed       = {self.title_row_removed}"
        out += "\n" + f"prefixing_performed     = {self.prefixing_performed}"
        out += "\n" + f"prefixed_rows           = {self.prefixed_rows}"
        out += "\n" + f"footnotes_copied        = {self.footnotes_copied}"
        out += "\n" + f"spanning_cells_extended = {self.spanning_cells_extended}"
        out += "\n" + f"header_extended_up      = {self.header_extended_up}"
        out += "\n" + f"header_extended_down    = {self.header_extended_down}"
        out += "\n" + f"table_transposed        = {self._table_transposed}"
        return out
