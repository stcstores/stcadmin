import pytest

from fba.forms import FBAShipmentDestinationForm
from inventory.forms.fieldtypes import SelectizeModelChoiceField


@pytest.fixture
def destination(fba_shipment_destination_factory):
    return fba_shipment_destination_factory.create()


@pytest.fixture
def form_data(destination):
    return {"destination": destination.id}


@pytest.mark.django_db
def test_destination_field(destination):
    form = FBAShipmentDestinationForm()
    assert isinstance(form.fields["destination"], SelectizeModelChoiceField)


@pytest.mark.django_db
def test_fields(destination):
    form = FBAShipmentDestinationForm()
    assert list(form.fields.keys()) == ["destination"]


@pytest.mark.django_db
def test_form_submission(destination):
    form = FBAShipmentDestinationForm({"destination": destination})
    assert form.is_valid()
    assert form.cleaned_data["destination"] == destination
