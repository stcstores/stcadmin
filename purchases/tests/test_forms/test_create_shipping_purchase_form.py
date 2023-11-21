from decimal import Decimal
from unittest import mock

import pytest

from purchases.forms import CreateShippingPurchaseForm


@pytest.fixture
def purchaser(staff_factory):
    return staff_factory.create()


@pytest.fixture
def price():
    return Decimal("34.32")


@pytest.fixture
def country(country_factory):
    return country_factory.create()


@pytest.fixture
def shipping_service(shipping_service_factory):
    return shipping_service_factory.create()


@pytest.fixture
def purchaseable_shipping_service(
    shipping_service, purchasable_shipping_service_factory
):
    purchasable_shipping_service_factory.create(shipping_service=shipping_service)


@pytest.fixture
def weight():
    return 500


@pytest.fixture
def form_data(
    purchaseable_shipping_service, purchaser, weight, country, shipping_service
):
    return {
        "purchaser": purchaser.id,
        "quantity": 2,
        "weight": weight,
        "country": country.id,
        "shipping_service": shipping_service.id,
    }


@pytest.fixture
def mock_purchase_model():
    with mock.patch("purchases.forms.models.ShippingPurchase") as mock_purchase_model:
        yield mock_purchase_model


@pytest.fixture
def purchase(shipping_purchase_factory):
    return shipping_purchase_factory.build()


@pytest.fixture
def saved_form(purchase):
    form = CreateShippingPurchaseForm()
    form.instance = purchase
    return form


def test_has_purchaser_field():
    assert "purchaser" in CreateShippingPurchaseForm().fields


def test_has_country_field():
    assert "country" in CreateShippingPurchaseForm().fields


def test_has_quantity_field():
    assert "quantity" in CreateShippingPurchaseForm().fields


def test_has_shipping_service_field():
    assert "shipping_service" in CreateShippingPurchaseForm().fields


def test_has_weight_field():
    assert "weight" in CreateShippingPurchaseForm().fields


@pytest.mark.django_db
def test_form_validation(form_data):
    form = CreateShippingPurchaseForm(form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_purchaser_in_cleaned_data(purchaser, form_data):
    form = CreateShippingPurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["purchaser"] == purchaser


@pytest.mark.django_db
def test_country_in_cleaned_data(country, form_data):
    form = CreateShippingPurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["country"] == country


@pytest.mark.django_db
def test_shipping_service_in_cleaned_data(shipping_service, form_data):
    form = CreateShippingPurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["shipping_service"] == shipping_service


@pytest.mark.django_db
def test_weight_in_cleaned_data(weight, form_data):
    form = CreateShippingPurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["weight"] == weight


@pytest.mark.django_db
def test_quantity_in_cleaned_data(form_data):
    form = CreateShippingPurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["quantity"] == form_data["quantity"]


@pytest.mark.django_db
def test_save_calls_new_purchase(
    mock_purchase_model,
    form_data,
    purchaser,
    country,
    shipping_service,
    weight,
):
    form = CreateShippingPurchaseForm(form_data)
    form.is_valid()
    form.save()
    mock_purchase_model.objects.new_purchase.assert_called_once_with(
        purchased_by=purchaser,
        country=country,
        shipping_service=shipping_service,
        weight=weight,
        quantity=form_data["quantity"],
    )


@pytest.mark.django_db
def test_save_sets_purchase_to_instance_attribute(mock_purchase_model, form_data):
    form = CreateShippingPurchaseForm(form_data)
    form.is_valid()
    form.save()
    assert form.instance == mock_purchase_model.objects.new_purchase.return_value
