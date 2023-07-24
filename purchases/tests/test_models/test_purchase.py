import datetime as dt
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from home.models import Staff
from inventory.models import Product
from purchases import models


@pytest.fixture
def purchase_settings(purchase_settings_factory):
    return purchase_settings_factory.create()


@pytest.fixture
def purchased_by(staff_factory):
    return staff_factory.create()


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def quantity():
    return 2


@pytest.fixture
def purchase(purchase_factory, purchased_by, product):
    purchase = purchase_factory.create(product=product, purchased_by=purchased_by)
    purchase.full_clean()
    return purchase


@pytest.fixture
def new_purchase(purchase_settings, purchased_by, product, quantity):
    return models.Purchase.objects.new_purchase(
        purchased_by=purchased_by, product=product, quantity=quantity
    )


@pytest.mark.django_db
def test_purchase_has_purchased_by_attribute(purchase):
    assert isinstance(purchase.purchased_by, Staff)


@pytest.mark.django_db
def test_purchase_has_product_attribute(purchase):
    assert isinstance(purchase.product, Product)


@pytest.mark.django_db
def test_purchase_has_quantity_attribute(purchase):
    assert isinstance(purchase.quantity, int)


@pytest.mark.django_db
def test_purchase_has_time_of_purchase_item_price_attribute(purchase):
    assert isinstance(purchase.time_of_purchase_item_price, int)


@pytest.mark.django_db
def test_purchase_has_time_of_purchase_charge_attribute(purchase):
    assert isinstance(purchase.time_of_purchase_charge, Decimal)


@pytest.mark.django_db
def test_purchase_price_has_export_attribute(purchase):
    assert isinstance(purchase.export, models.PurchaseExport)


@pytest.mark.django_db
def test_purchase_price_has_created_at_attribute(purchase):
    assert isinstance(purchase.created_at, dt.datetime)


@pytest.mark.django_db
def test_purchase_price_has_modified_at_attribute(purchase):
    assert isinstance(purchase.modified_at, dt.datetime)


@pytest.mark.django_db
def test_new_purchase_sets_purchased_by(new_purchase, purchased_by):
    assert new_purchase.purchased_by == purchased_by


@pytest.mark.django_db
def test_new_purchase_sets_product(new_purchase, product):
    assert new_purchase.product == product


@pytest.mark.django_db
def test_new_purchase_sets_quantity(new_purchase, quantity):
    assert new_purchase.quantity == quantity


@pytest.mark.django_db
def test_new_purchase_sets_time_of_purchase_item_price(new_purchase, product):
    assert new_purchase.time_of_purchase_item_price == product.purchase_price


@pytest.mark.django_db
def test_new_purchase_sets_time_of_purchase_charge(purchase_settings, new_purchase):
    assert new_purchase.time_of_purchase_charge == purchase_settings.purchase_charge


@pytest.mark.django_db
def test_new_purchase_does_not_set_export(purchase_settings, new_purchase):
    assert new_purchase.export is None


@pytest.mark.django_db
def test_to_pay_method(purchase_factory):
    purchase = purchase_factory.create(
        quantity=2, time_of_purchase_item_price=500, time_of_purchase_charge=1.30
    )
    assert purchase.to_pay() == 1300


@pytest.mark.django_db
def test_cannot_create_purchase_with_zero_quantity(
    purchase_settings, purchased_by, product
):
    with pytest.raises(ValidationError):
        models.Purchase.objects.new_purchase(
            purchased_by=purchased_by, product=product, quantity=0
        )
