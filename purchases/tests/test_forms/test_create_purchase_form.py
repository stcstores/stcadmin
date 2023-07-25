from unittest import mock

import pytest

from purchases.forms import CreatePurchaseForm


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def purchaser(staff_factory):
    return staff_factory.create()


@pytest.fixture
def form_data(purchaser, product):
    return {"purchaser": purchaser.id, "product_id": product.id, "quantity": 2}


@pytest.fixture
def mock_purchase_model():
    with mock.patch("purchases.forms.models.Purchase") as mock_purchase_model:
        yield mock_purchase_model


def test_has_purchaser_field():
    assert "purchaser" in CreatePurchaseForm().fields


def test_has_product_field():
    assert "product_id" in CreatePurchaseForm().fields


def test_has_quantity_field():
    assert "quantity" in CreatePurchaseForm().fields


@pytest.mark.django_db
def test_form_validation(form_data):
    form = CreatePurchaseForm(form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_purchaser_in_cleaned_data(purchaser, form_data):
    form = CreatePurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["purchaser"] == purchaser


@pytest.mark.django_db
def test_product_in_cleaned_data(product, form_data):
    form = CreatePurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["product_id"] == product.pk


@pytest.mark.django_db
def test_quantity_in_cleaned_data(form_data):
    form = CreatePurchaseForm(form_data)
    form.is_valid()
    assert form.cleaned_data["quantity"] == form_data["quantity"]


@pytest.mark.django_db
def test_save_calls_new_purchase(mock_purchase_model, form_data, purchaser, product):
    form = CreatePurchaseForm(form_data)
    form.is_valid()
    form.save()
    mock_purchase_model.objects.new_purchase.assert_called_once_with(
        purchased_by=purchaser, product=product, quantity=form_data["quantity"]
    )
