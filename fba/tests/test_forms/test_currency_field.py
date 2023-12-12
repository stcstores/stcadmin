import pytest

from fba.forms import CurrencyField, CurrencyWidget


@pytest.fixture
def field():
    return CurrencyField()


def test_widget(field):
    assert field.widget_class == CurrencyWidget


@pytest.mark.parametrize("value,expected", (("5.54", 554), ("0.02", 2), (54, 5400)))
def test_to_python(value, expected, field):
    assert field.to_python(value) == expected
