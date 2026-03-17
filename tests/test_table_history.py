"""Tests for chemtabextract.table.history.History.

History is a simple boolean-flag object; its property getters and __repr__
were entirely uncovered (lines 33, 43, 48, 56, 62, 68, 76–85 in the
coverage report for commit f2edc1f).  These tests cover:

  - all eight boolean properties return False by default
  - setting each private attribute to True is reflected in the property
  - __repr__ includes every property name and its current value
  - History integrates correctly with Table: table_transposed is False on
    a freshly built Table and True after transpose()
"""

import pytest

from chemtabextract import Table
from chemtabextract.table.history import History


class TestHistoryDefaults:
    """All History flags must be False immediately after construction."""

    def test_title_row_removed_default_is_false(self) -> None:
        """title_row_removed should be False on a fresh History."""
        assert History().title_row_removed is False

    def test_prefixing_performed_default_is_false(self) -> None:
        """prefixing_performed should be False on a fresh History."""
        assert History().prefixing_performed is False

    def test_prefixed_rows_default_is_false(self) -> None:
        """prefixed_rows should be False on a fresh History."""
        assert History().prefixed_rows is False

    def test_footnotes_copied_default_is_false(self) -> None:
        """footnotes_copied should be False on a fresh History."""
        assert History().footnotes_copied is False

    def test_spanning_cells_extended_default_is_false(self) -> None:
        """spanning_cells_extended should be False on a fresh History."""
        assert History().spanning_cells_extended is False

    def test_header_extended_up_default_is_false(self) -> None:
        """header_extended_up should be False on a fresh History."""
        assert History().header_extended_up is False

    def test_header_extended_down_default_is_false(self) -> None:
        """header_extended_down should be False on a fresh History."""
        assert History().header_extended_down is False

    def test_table_transposed_default_is_false(self) -> None:
        """table_transposed should be False on a fresh History."""
        assert History().table_transposed is False


class TestHistoryPropertySetters:
    """Each property correctly reflects its backing private attribute."""

    @pytest.mark.parametrize(
        ("private_attr", "public_prop"),
        [
            ("_title_row_removed", "title_row_removed"),
            ("_prefixing_performed", "prefixing_performed"),
            ("_prefixed_rows", "prefixed_rows"),
            ("_footnotes_copied", "footnotes_copied"),
            ("_spanning_cells_extended", "spanning_cells_extended"),
            ("_header_extended_up", "header_extended_up"),
            ("_header_extended_down", "header_extended_down"),
            ("_table_transposed", "table_transposed"),
        ],
        ids=[
            "title_row_removed",
            "prefixing_performed",
            "prefixed_rows",
            "footnotes_copied",
            "spanning_cells_extended",
            "header_extended_up",
            "header_extended_down",
            "table_transposed",
        ],
    )
    def test_property_reflects_private_attribute(self, private_attr: str, public_prop: str) -> None:
        """Setting the private attribute to True should be visible via the property."""
        h = History()
        setattr(h, private_attr, True)
        assert getattr(h, public_prop) is True


class TestHistoryRepr:
    """__repr__ should include every property name and its current value."""

    def test_repr_returns_string(self) -> None:
        """repr(History()) should return a str, not raise."""
        assert isinstance(repr(History()), str)

    @pytest.mark.parametrize(
        "expected_name",
        [
            "title_row_removed",
            "prefixing_performed",
            "prefixed_rows",
            "footnotes_copied",
            "spanning_cells_extended",
            "header_extended_up",
            "header_extended_down",
            "table_transposed",
        ],
    )
    def test_repr_contains_property_name(self, expected_name: str) -> None:
        """repr() output should contain the property name for every flag."""
        assert expected_name in repr(History())

    def test_repr_shows_false_for_fresh_history(self) -> None:
        """repr() of a fresh History should contain 'False' for all flags."""
        r = repr(History())
        assert r.count("False") == 8

    def test_repr_reflects_updated_flag(self) -> None:
        """repr() should show True once a flag is set via the public setter."""
        h = History()
        h.set_table_transposed(True)
        assert "True" in repr(h)


class TestHistorySetterApi:
    """Each set_*() method must update its backing attribute via the public setter.

    These tests exercise the setter API introduced in Q3 directly — calling
    the setter method and asserting the public property reflects the result.
    This is distinct from ``TestHistoryPropertySetters``, which validates the
    property getters by bypassing the setter (testing the underlying attribute
    access directly).
    """

    _SETTER_PROP_PAIRS = [
        ("set_title_row_removed", "title_row_removed"),
        ("set_prefixing_performed", "prefixing_performed"),
        ("set_prefixed_rows", "prefixed_rows"),
        ("set_footnotes_copied", "footnotes_copied"),
        ("set_spanning_cells_extended", "spanning_cells_extended"),
        ("set_header_extended_up", "header_extended_up"),
        ("set_header_extended_down", "header_extended_down"),
        ("set_table_transposed", "table_transposed"),
    ]

    @pytest.mark.parametrize(
        ("setter_name", "prop_name"),
        _SETTER_PROP_PAIRS,
        ids=[pair[1] for pair in _SETTER_PROP_PAIRS],
    )
    def test_setter_true_reflected_in_property(self, setter_name: str, prop_name: str) -> None:
        """Calling set_*(True) should be immediately visible via the property."""
        h = History()
        getattr(h, setter_name)(True)
        assert getattr(h, prop_name) is True

    @pytest.mark.parametrize(
        ("setter_name", "prop_name"),
        _SETTER_PROP_PAIRS,
        ids=[pair[1] for pair in _SETTER_PROP_PAIRS],
    )
    def test_setter_false_resets_property(self, setter_name: str, prop_name: str) -> None:
        """Calling set_*(False) after set_*(True) should reset the property."""
        h = History()
        getattr(h, setter_name)(True)
        getattr(h, setter_name)(False)
        assert getattr(h, prop_name) is False

    def test_repr_reflects_flag_set_via_setter(self) -> None:
        """repr() should show True for a flag set via the setter method."""
        h = History()
        h.set_table_transposed(True)
        assert "True" in repr(h)


class TestHistoryTableIntegration:
    """History integrates correctly with Table."""

    def test_fresh_table_table_transposed_is_false(self) -> None:
        """A newly constructed Table should report table_transposed=False."""
        table = Table("./tests/data/table_example1.csv")
        assert table.history.table_transposed is False

    def test_table_transposed_is_true_after_transpose(self) -> None:
        """table_transposed should be True after calling Table.transpose()."""
        table = Table("./tests/data/table_example1.csv")
        table.transpose()
        assert table.history.table_transposed is True

    def test_history_object_replaced_after_transpose(self) -> None:
        """transpose() creates a new History instance; the old object is discarded."""
        table = Table("./tests/data/table_example1.csv")
        original_history = table.history
        table.transpose()
        assert table.history is not original_history
