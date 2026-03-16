"""
Inputs from python list object.
"""

import logging

import numpy as np

log = logging.getLogger(__name__)


def read(plist):
    """
    Creates a numpy array from a Python list. Works if rows are of different length.

    :param plist: Input List
    :type plist: list
    :return: numpy.ndarray
    """
    length = len(sorted(plist, key=len, reverse=True)[0])
    array = np.array([row + [None] * (length - len(row)) for row in plist], dtype="<U60")
    return array
