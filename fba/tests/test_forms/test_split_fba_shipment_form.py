import pytest

from fba.forms import SplitFBAOrderShipmentForm


@pytest.fixture
def form_data():
    return {
        "length_cm": 1,
        "width_cm": 2,
        "height_cm": 3,
        "weight": 4,
        "quantity": 5,
        "value": 5.50,
    }


def test_fields():
    form = SplitFBAOrderShipmentForm()
    assert list(form.fields.keys()) == [
        "length_cm",
        "width_cm",
        "height_cm",
        "weight",
        "quantity",
        "value",
    ]


def test_cleaned_data(form_data):
    form = SplitFBAOrderShipmentForm(form_data)
    assert form.is_valid() is True
    assert form.cleaned_data == form_data
