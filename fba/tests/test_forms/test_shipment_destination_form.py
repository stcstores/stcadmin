import pytest

from fba.forms import ShipmentDestinationForm
from fba.models import FBAShipmentDestination


@pytest.fixture
def form_data():
    return {
        "name": "A",
        "recipient_name": "B",
        "contact_telephone": "C",
        "address_line_1": "D",
        "address_line_2": "E",
        "address_line_3": "F",
        "city": "G",
        "state": "H",
        "country": "I",
        "country_iso": "J",
        "postcode": "K",
    }


def test_fields():
    form = ShipmentDestinationForm()
    assert list(form.fields.keys()) == [
        "name",
        "recipient_name",
        "contact_telephone",
        "address_line_1",
        "address_line_2",
        "address_line_3",
        "city",
        "state",
        "country",
        "country_iso",
        "postcode",
    ]


@pytest.mark.django_db
def test_creation_with_form(form_data):
    form = ShipmentDestinationForm(form_data)
    assert form.is_valid() is True
    form.save()
    assert FBAShipmentDestination.objects.filter(**form_data).exists() is True


@pytest.mark.django_db
def test_update_with_form(fba_shipment_destination_factory, form_data):
    destination = fba_shipment_destination_factory.create()
    form = ShipmentDestinationForm(form_data, instance=destination)
    assert form.is_valid() is True
    form.save()
    assert destination.name == form_data["name"]
    assert destination.recipient_name == form_data["recipient_name"]
    assert destination.contact_telephone == form_data["contact_telephone"]
    assert destination.address_line_1 == form_data["address_line_1"]
    assert destination.address_line_2 == form_data["address_line_2"]
    assert destination.address_line_3 == form_data["address_line_3"]
    assert destination.city == form_data["city"]
    assert destination.state == form_data["state"]
    assert destination.country == form_data["country"]
    assert destination.country_iso == form_data["country_iso"]
    assert destination.postcode == form_data["postcode"]
