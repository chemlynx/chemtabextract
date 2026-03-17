"""
Exceptions defined for chemtabextract.
"""


class TDEError(Exception):
    """
    Base class for exceptions in chemtabextract.
    """


class InputError(TDEError):
    """
    Exception raised for errors in the input.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class MIPSError(TDEError):
    """
    Exception raised for failure of the main MIPS algorithm.
    Usually signals that the table is broken or not well structured.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message
