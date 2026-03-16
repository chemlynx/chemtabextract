# vulture whitelist — public API symbols that are used by downstream consumers
# but not referenced within the library itself.
# See: https://github.com/jendrikseipp/vulture#whitelists
#
# All imports must stay at the top to satisfy ruff E402.
# Selenium imports are omitted here because they are only available with the
# [web] extra — their 90%-confidence vulture hits in from_html.py are accepted
# as false positives given the conditional import guard.

from chemtabextract.output.print import print_table  # noqa: F401
from chemtabextract.output.to_pandas import print_category_table  # noqa: F401
from chemtabextract.table.algorithms._categorize import categorize_header  # noqa: F401
from chemtabextract.table.parse import CellParser
from chemtabextract.table.table import Table

# Public Table methods accessed by downstream consumers and tests.
Table.subtables
Table.row_categories
Table.contains
Table.transpose
Table.print_raw_table
Table.to_csv

# CellParser.cut is part of the parser public interface.
CellParser.cut

# print_table uses .field_names on the PrettyTable instance at runtime.
print_table
