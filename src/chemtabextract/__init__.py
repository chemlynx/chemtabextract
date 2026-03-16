# -*- coding: utf-8 -*-
"""
chemtabextract
Extracts and standardises structured data from scientific tables.
Algorithm from David W. Embley et al., DOI: 10.1007/s10032-016-0259-1
~~~~~~~~~~~~~~~~~
"""

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

from chemtabextract.exceptions import TDEError, InputError, MIPSError  # noqa: E402
from chemtabextract.table.table import Table, TrivialTable  # noqa: E402
