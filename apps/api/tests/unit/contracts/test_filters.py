from datetime import date

import pytest
from pydantic import ValidationError

from app.contracts.filters import ListFilters, validate_sort_field


def test_filter_defaults_are_predictable() -> None:
    filters = ListFilters()
    assert filters.page == 1
    assert filters.page_size == 25
    assert filters.sort_by == "created_at"
    assert filters.sort_order == "desc"
    assert filters.archived is False


def test_date_range_rejects_reverse_order() -> None:
    with pytest.raises(ValidationError, match="date_from must be on or before date_to"):
        ListFilters(date_from=date(2026, 7, 12), date_to=date(2026, 7, 11))


def test_sort_field_requires_an_allowlist() -> None:
    allowed = frozenset({"created_at", "name"})
    assert validate_sort_field("name", allowed) == "name"
    with pytest.raises(ValueError, match="sort_by must be one of"):
        validate_sort_field("password_hash", allowed)
