import pytest
from django import forms

from fba.forms import PackageForm
from fba.models import FBAShipmentPackage


@pytest.fixture
def shipment_order(fba_shipment_order_factory):
    return fba_shipment_order_factory.create()


@pytest.fixture
def form_data(shipment_order):
    return {
        "shipment_order": shipment_order.id,
        "length_cm": 1,
        "width_cm": 2,
        "height_cm": 3,
    }


def test_shipment_order_field_widget():
    form = PackageForm()
    assert isinstance(form.fields["shipment_order"].widget, forms.HiddenInput)


def test_fields():
    form = PackageForm()
    assert list(form.fields.keys()) == [
        "shipment_order",
        "length_cm",
        "width_cm",
        "height_cm",
    ]


@pytest.mark.django_db
def test_creation_with_form(form_data, shipment_order):
    form = PackageForm(form_data)
    assert form.is_valid() is True
    form.save()
    assert (
        FBAShipmentPackage.objects.filter(
            shipment_order=shipment_order,
            length_cm=form_data["length_cm"],
            width_cm=form_data["width_cm"],
            height_cm=form_data["height_cm"],
        ).exists()
        is True
    )


@pytest.mark.django_db
def test_update_with_form(fba_shipment_package_factory, form_data, shipment_order):
    package = fba_shipment_package_factory.create()
    form = PackageForm(form_data, instance=package)
    assert form.is_valid() is True
    form.save()
    assert package.shipment_order == shipment_order
    assert package.length_cm == form_data["length_cm"]
    assert package.width_cm == form_data["width_cm"]
    assert package.height_cm == form_data["height_cm"]
