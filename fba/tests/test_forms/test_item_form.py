import pytest
from django import forms

from fba.forms import CurrencyWidget, ItemForm
from fba.models import FBAShipmentItem


@pytest.fixture
def package(fba_shipment_package_factory):
    return fba_shipment_package_factory.create()


@pytest.fixture
def form_data(package):
    return {
        "package": package.id,
        "sku": "A",
        "description": "B",
        "quantity": 5,
        "weight_kg": 2.5,
        "value": 5.50,
        "country_of_origin": "C",
        "hr_code": "D",
    }


def test_shipment_order_field_widget():
    form = ItemForm()
    assert isinstance(form.fields["value"].widget, CurrencyWidget)


def test_description_field_widget():
    form = ItemForm()
    assert isinstance(form.fields["description"].widget, forms.Textarea)


def test_fields():
    form = ItemForm()
    assert list(form.fields.keys()) == [
        "package",
        "sku",
        "description",
        "quantity",
        "weight_kg",
        "value",
        "country_of_origin",
        "hr_code",
    ]


@pytest.mark.django_db
def test_creation_with_form(form_data, package):
    form = ItemForm(form_data)
    assert form.is_valid() is True
    form.save()
    assert (
        FBAShipmentItem.objects.filter(
            package=package,
            sku=form_data["sku"],
            description=form_data["description"],
            quantity=form_data["quantity"],
            weight_kg=form_data["weight_kg"],
            value=550,
            country_of_origin=form_data["country_of_origin"],
            hr_code=form_data["hr_code"],
        ).exists()
        is True
    )


@pytest.mark.django_db
def test_update_with_form(fba_shipment_item_factory, form_data, package):
    item = fba_shipment_item_factory.create()
    form = ItemForm(form_data, instance=item)
    assert form.is_valid() is True
    form.save()
    assert item.package == package
    assert item.sku == form_data["sku"]
    assert item.description == form_data["description"]
    assert item.quantity == form_data["quantity"]
    assert item.weight_kg == form_data["weight_kg"]
    assert item.value == 550
    assert item.country_of_origin == form_data["country_of_origin"]
    assert item.hr_code == form_data["hr_code"]
