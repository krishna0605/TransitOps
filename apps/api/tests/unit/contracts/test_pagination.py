import pytest
from pydantic import ValidationError

from app.contracts.dto.common import Page
from app.contracts.pagination import PageParams


def test_pagination_defaults() -> None:
    assert PageParams().model_dump() == {"page": 1, "page_size": 25}


@pytest.mark.parametrize("page_size", [0, 101])
def test_page_size_boundaries(page_size: int) -> None:
    with pytest.raises(ValidationError):
        PageParams(page_size=page_size)


def test_page_contract() -> None:
    page = Page[str](items=["one"], page=1, page_size=25, total=1)
    assert page.model_dump() == {"items": ["one"], "page": 1, "page_size": 25, "total": 1}
