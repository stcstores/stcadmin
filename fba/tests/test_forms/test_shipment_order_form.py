import pytest

from fba.forms import ShipmentOrderForm
from fba.models import FBAShipmentOrder


@pytest.fixture
def destination(fba_shipment_destination_factory):
    return fba_shipment_destination_factory.create()


@pytest.fixture
def shipment_method(fba_shipment_method_factory):
    return fba_shipment_method_factory.create()


@pytest.fixture
def user(user_factory):
    return user_factory.create()


@pytest.fixture
def form_data(destination, shipment_method, user):
    return {
        "destination": destination.id,
        "shipment_method": shipment_method.id,
        "user": user.id,
        "at_risk": "on",
        "planned_shipment_date": "2024-05-04",
    }


def test_fields():
    form = ShipmentOrderForm()
    assert list(form.fields.keys()) == [
        "destination",
        "shipment_method",
        "user",
        "planned_shipment_date",
        "at_risk",
    ]


@pytest.mark.django_db
def test_creation_with_form(form_data, destination, shipment_method, user):
    form = ShipmentOrderForm(form_data)
    assert form.is_valid() is True
    form.save()
    assert (
        FBAShipmentOrder.objects.filter(
            export__isnull=True,
            destination=destination,
            shipment_method=shipment_method,
            user=user,
        ).exists()
        is True
    )


@pytest.mark.django_db
def test_update_with_form(
    fba_shipment_order_factory, form_data, destination, shipment_method, user
):
    order = fba_shipment_order_factory.create()
    form = ShipmentOrderForm(form_data, instance=order)
    assert form.is_valid() is True
    form.save()
    assert order.destination == destination
    assert order.shipment_method == shipment_method
    assert order.user == user
