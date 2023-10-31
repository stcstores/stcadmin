import pytest

from fba.forms import CurrencyWidget


@pytest.fixture
def widget():
    return CurrencyWidget()


def test_type(widget):
    assert widget.input_type == "number"


def test_step_attr(widget):
    assert widget.attrs["step"] == "0.01"


@pytest.mark.parametrize(
    "value,expected",
    (
        (512, "5.12"),
        (2, "0.02"),
        ("", None),
        (None, None),
    ),
)
def test_format_value(value, expected, widget):
    assert widget.format_value(value) == expected
