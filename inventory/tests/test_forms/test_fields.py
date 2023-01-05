import pytest

from inventory.forms import fields


@pytest.mark.parametrize(
    "input,expected",
    (
        ("word", "word"),
        ("word ", "word"),
        ("word&nbsp;word", "word word"),
        ("word  word", "word word"),
        ("word\nword", "word\nword"),
    ),
)
def test_description_field_clean_method(input, expected):
    assert fields.Description().clean(input) == expected
