from decimal import Decimal
from unittest import mock

import pytest

from purchases.forms import CreateOtherPurchaseForm


@pytest.fixture
def description():
    return "A thing that isn't in the inventory"


@pytest.fixture
def purchaser(staff_factory):
    return staff_factory.create()


@pytest.fixture
def price():
    return Decimal("34.32")


@pytest.fixture
def form_data(purchaser, description, price):
    return {
        "purchaser": purchaser.id,
        "description": description,
        "quantity": 2,
        "price": float(price),
    }


@pytest.fixture
def mock_purchase_model():
    with mock.patch("purchases.forms.models.OtherPurchase") as mock_purchase_model:
        yield mock_purchase_model


@pytest.fixture
def purchase(other_purchase_factory):
    return other_purchase_factory.build()


@pytest.fixture
def saved_form(purchase):
    form = CreateOtherPurchaseForm()
    form.instance = purchase
    return form


def test_has_purchaser_field():
    assert "purchaser" in CreateOtherPurchaseForm().fields


def test_has_description_field():
    assert "description" in CreateOtherPurchaseForm().fields


def test_has_quantity_field():
    assert "quantity" in CreateOtherPurchaseForm().fields


def test_has_price_field():
    assert "price" in CreateOtherPurchaseForm().fields


@pytest.mark.django_db
def test_form_validation(form_data):
    form = CreateOtherPurchaseForm(form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_purchaser_in_cleaned_data(purchaser, form_data):
    form = CreateOtherPurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["purchaser"] == purchaser


@pytest.mark.django_db
def test_description_in_cleaned_data(description, form_data):
    form = CreateOtherPurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["description"] == description


@pytest.mark.django_db
def test_price_in_cleaned_data(price, form_data):
    form = CreateOtherPurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["price"] == price


@pytest.mark.django_db
def test_quantity_in_cleaned_data(form_data):
    form = CreateOtherPurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["quantity"] == form_data["quantity"]


@pytest.mark.django_db
def test_save_calls_new_purchase(
    mock_purchase_model, form_data, purchaser, description, price
):
    form = CreateOtherPurchaseForm(form_data)
    form.is_valid()
    form.save()
    mock_purchase_model.objects.new_purchase.assert_called_once_with(
        purchased_by=purchaser,
        description=description,
        price=price,
        quantity=form_data["quantity"],
    )


@pytest.mark.django_db
def test_save_sets_purchase_to_instance_attribute(mock_purchase_model, form_data):
    form = CreateOtherPurchaseForm(form_data)
    form.is_valid()
    form.save()
    assert form.instance == mock_purchase_model.objects.new_purchase.return_value
