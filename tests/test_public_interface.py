"""Smoke tests for the chemtabextract public interface.

Verifies that all exported symbols are importable from the top-level package,
that exception classes behave correctly, and that importing chemtabextract
does not create any log files.
"""

import importlib
import logging

import pytest


def test_top_level_imports() -> None:
    """All five public symbols are importable from chemtabextract directly."""
    from chemtabextract import InputError, MIPSError, Table, TDEError, TrivialTable

    assert Table is not None
    assert TrivialTable is not None
    assert issubclass(TrivialTable, Table)
    assert issubclass(InputError, TDEError)
    assert issubclass(MIPSError, TDEError)


def test_exception_importable_from_submodule() -> None:
    """Exceptions remain importable from chemtabextract.exceptions."""
    from chemtabextract.exceptions import InputError, MIPSError, TDEError

    assert issubclass(InputError, TDEError)
    assert issubclass(MIPSError, TDEError)


def test_nullhandler_installed() -> None:
    """chemtabextract installs a NullHandler and does not configure root logging."""

    pkg_logger = logging.getLogger("chemtabextract")
    handler_types = [type(h) for h in pkg_logger.handlers]
    assert logging.NullHandler in handler_types


def test_no_log_file_created(tmp_path, monkeypatch) -> None:
    """Importing chemtabextract must not create tde_log.txt."""
    monkeypatch.chdir(tmp_path)
    import chemtabextract  # noqa: F401

    importlib.reload(chemtabextract)
    assert not (tmp_path / "tde_log.txt").exists()


class TestInputError:
    """Tests for the InputError exception class."""

    def test_input_error_stores_message(self) -> None:
        """InputError should store its argument on the .message attribute."""
        from chemtabextract.exceptions import InputError

        err = InputError("bad input")
        assert err.message == "bad input"

    def test_input_error_is_catchable_as_tde_error(self) -> None:
        """InputError should be catchable via its TDEError base class."""
        from chemtabextract.exceptions import InputError, TDEError

        with pytest.raises(TDEError):
            raise InputError("bad input")

    def test_input_error_is_catchable_as_base_exception(self) -> None:
        """InputError should be catchable as a plain Exception."""
        from chemtabextract.exceptions import InputError

        with pytest.raises(Exception):
            raise InputError("bad input")


class TestMIPSError:
    """Tests for the MIPSError exception class."""

    def test_mips_error_stores_message(self) -> None:
        """MIPSError should store its argument on the .message attribute."""
        from chemtabextract.exceptions import MIPSError

        err = MIPSError("algorithm failed")
        assert err.message == "algorithm failed"

    def test_mips_error_is_catchable_as_tde_error(self) -> None:
        """MIPSError should be catchable via its TDEError base class."""
        from chemtabextract.exceptions import MIPSError, TDEError

        with pytest.raises(TDEError):
            raise MIPSError("algorithm failed")

    def test_mips_error_is_catchable_as_base_exception(self) -> None:
        """MIPSError should be catchable as a plain Exception."""
        from chemtabextract.exceptions import MIPSError

        with pytest.raises(Exception):
            raise MIPSError("algorithm failed")
