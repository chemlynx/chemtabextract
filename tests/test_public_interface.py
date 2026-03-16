"""Smoke tests for the chemtabextract public interface.

Verifies that all exported symbols are importable from the top-level package
and that importing chemtabextract does not create any log files.
"""

import importlib
import logging


def test_top_level_imports() -> None:
    """All five public symbols are importable from chemtabextract directly."""
    from chemtabextract import Table, TrivialTable
    from chemtabextract import TDEError, InputError, MIPSError

    assert Table is not None
    assert TrivialTable is not None
    assert issubclass(TrivialTable, Table)
    assert issubclass(InputError, TDEError)
    assert issubclass(MIPSError, TDEError)


def test_exception_importable_from_submodule() -> None:
    """Exceptions remain importable from chemtabextract.exceptions."""
    from chemtabextract.exceptions import TDEError, InputError, MIPSError

    assert issubclass(InputError, TDEError)
    assert issubclass(MIPSError, TDEError)


def test_nullhandler_installed() -> None:
    """chemtabextract installs a NullHandler and does not configure root logging."""
    import chemtabextract

    pkg_logger = logging.getLogger("chemtabextract")
    handler_types = [type(h) for h in pkg_logger.handlers]
    assert logging.NullHandler in handler_types


def test_no_log_file_created(tmp_path, monkeypatch) -> None:
    """Importing chemtabextract must not create tde_log.txt."""
    monkeypatch.chdir(tmp_path)
    import chemtabextract  # noqa: F401

    importlib.reload(chemtabextract)
    assert not (tmp_path / "tde_log.txt").exists()
