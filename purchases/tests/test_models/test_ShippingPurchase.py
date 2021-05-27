import datetime

import pytest

from purchases import models


@pytest.fixture
def shipping_price(shipping_price_factory):
    return shipping_price_factory.create()


@pytest.fixture
def to_pay():
    return 0


@pytest.fixture
def purchase_user(user_factory):
    return user_factory.create()


@pytest.fixture
def created_by(user_factory):
    return user_factory.create()


@pytest.fixture
def new_shipping_purchase(to_pay, purchase_user, created_by, shipping_price):
    purchase_note = models.ShippingPurchase(
        user=purchase_user,
        created_by=created_by,
        to_pay=to_pay,
        shipping_price=shipping_price,
    )
    purchase_note.save()
    return purchase_note


@pytest.mark.django_db
def test_sets_user(purchase_user, new_shipping_purchase):
    assert new_shipping_purchase.user == purchase_user


@pytest.mark.django_db
def test_sets_created_at(new_shipping_purchase):
    assert isinstance(new_shipping_purchase.created_at, datetime.datetime)


@pytest.mark.django_db
def test_sets_modified_at(new_shipping_purchase):
    assert isinstance(new_shipping_purchase.modified_at, datetime.datetime)


@pytest.mark.django_db
def test_sets_created_by(created_by, new_shipping_purchase):
    assert new_shipping_purchase.created_by == created_by


@pytest.mark.django_db
def test_sets_to_pay(to_pay, new_shipping_purchase):
    assert new_shipping_purchase.to_pay == to_pay


@pytest.mark.django_db
def test_sets_cancelled(new_shipping_purchase):
    assert new_shipping_purchase.cancelled is False


@pytest.mark.django_db
def test_sets_shipping_price(new_shipping_purchase, shipping_price):
    assert new_shipping_purchase.shipping_price == shipping_price
