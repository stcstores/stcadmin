import datetime as dt
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from home.models import Staff
from purchases import models


@pytest.fixture
def purchased_by(staff_factory):
    return staff_factory.create()


@pytest.fixture
def description():
    return "Purchased Item Description"


@pytest.fixture
def quantity():
    return 2


@pytest.fixture
def price():
    return Decimal("50.32")


@pytest.fixture
def purchase(other_purchase_factory, purchased_by, description):
    purchase = other_purchase_factory.create(
        description=description, purchased_by=purchased_by
    )
    return purchase


@pytest.mark.django_db
def test_full_clean(purchase):
    assert purchase.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_purchase_has_purchased_by_attribute(purchase):
    assert isinstance(purchase.purchased_by, Staff)


@pytest.mark.django_db
def test_purchase_has_description_attribute(purchase):
    assert isinstance(purchase.description, str)


@pytest.mark.django_db
def test_purchase_has_quantity_attribute(purchase):
    assert isinstance(purchase.quantity, int)


@pytest.mark.django_db
def test_purchase_has_tprice_attribute(purchase):
    assert isinstance(purchase.price, Decimal)


@pytest.mark.django_db
def test_purchase_price_has_export_attribute(purchase):
    assert isinstance(purchase.export, models.PurchaseExport)


@pytest.mark.django_db
def test_purchase_price_has_created_at_attribute(purchase):
    assert isinstance(purchase.created_at, dt.datetime)


@pytest.mark.django_db
def test_purchase_price_has_modified_at_attribute(purchase):
    assert isinstance(purchase.modified_at, dt.datetime)


# Test Methods


@pytest.mark.django_db
def test_to_pay_method(purchase):
    purchase.quantity = 2
    purchase.price = Decimal("15.22")
    assert purchase.to_pay() == 30.44


@pytest.mark.django_db
def test_str_method(other_purchase_factory):
    purchase = other_purchase_factory.create(
        purchased_by__first_name="Joe",
        purchased_by__second_name="Man",
        quantity=2,
    )
    assert str(purchase) == "2 X Other Purchase for Joe Man"


@pytest.mark.django_db
def test_get_absolute_url_method(purchase):
    assert purchase.get_absolute_url() == reverse(
        "purchases:update_other_purchase", args=[purchase.pk]
    )


@pytest.mark.django_db
def test_item_price_property(purchase):
    purchase.price = Decimal("5.22")
    assert purchase.item_price == 5.22


# Test Manager


@pytest.fixture
def new_purchase(purchased_by, description, quantity, price):
    return models.OtherPurchase.objects.new_purchase(
        purchased_by=purchased_by,
        description=description,
        quantity=quantity,
        price=price,
    )


@pytest.mark.django_db
def test_new_purchase_sets_purchased_by(new_purchase, purchased_by):
    assert new_purchase.purchased_by == purchased_by


@pytest.mark.django_db
def test_new_purchase_sets_product(new_purchase, description):
    assert new_purchase.description == description


@pytest.mark.django_db
def test_new_purchase_sets_quantity(new_purchase, quantity):
    assert new_purchase.quantity == quantity


@pytest.mark.django_db
def test_new_purchase_sets_price(new_purchase, price):
    assert new_purchase.price == price


@pytest.mark.django_db
def test_new_purchase_does_not_set_export(new_purchase):
    assert new_purchase.export is None


@pytest.mark.django_db
def test_cannot_create_product_purchase_with_zero_quantity(
    purchased_by, description, price
):
    with pytest.raises(ValidationError):
        models.OtherPurchase.objects.new_purchase(
            purchased_by=purchased_by, description=description, quantity=0, price=price
        )
