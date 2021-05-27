import datetime

import pytest
from django.core.exceptions import ValidationError

from purchases import models


@pytest.fixture
def product_id():
    return "894135456"


@pytest.fixture
def product_sku():
    return "ABC-DEF-123"


@pytest.fixture
def product_name():
    return "Test Stock Product Name"


@pytest.fixture
def full_price():
    return 2460


@pytest.fixture
def discount_percentage():
    return 20


@pytest.fixture
def quantity():
    return 5


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
def new_stock_purchase(
    to_pay,
    purchase_user,
    created_by,
    product_id,
    product_sku,
    product_name,
    full_price,
    discount_percentage,
    quantity,
):
    stock_purchase = models.StockPurchase(
        user=purchase_user,
        created_by=created_by,
        to_pay=to_pay,
        product_id=product_id,
        product_sku=product_sku,
        product_name=product_name,
        full_price=full_price,
        discount_percentage=discount_percentage,
        quantity=quantity,
    )
    stock_purchase.save()
    return stock_purchase


@pytest.mark.django_db
def test_sets_user(purchase_user, new_stock_purchase):
    assert new_stock_purchase.user == purchase_user


@pytest.mark.django_db
def test_sets_created_at(new_stock_purchase):
    assert isinstance(new_stock_purchase.created_at, datetime.datetime)


@pytest.mark.django_db
def test_sets_modified_at(new_stock_purchase):
    assert isinstance(new_stock_purchase.modified_at, datetime.datetime)


@pytest.mark.django_db
def test_sets_created_by(created_by, new_stock_purchase):
    assert new_stock_purchase.created_by == created_by


@pytest.mark.django_db
def test_sets_to_pay(to_pay, new_stock_purchase):
    assert new_stock_purchase.to_pay == to_pay


@pytest.mark.django_db
def test_sets_product_id(new_stock_purchase, product_id):
    assert new_stock_purchase.product_id == product_id


@pytest.mark.django_db
def test_sets_product_sku(new_stock_purchase, product_sku):
    assert new_stock_purchase.product_sku == product_sku


@pytest.mark.django_db
def test_sets_product_name(new_stock_purchase, product_name):
    assert new_stock_purchase.product_name == product_name


@pytest.mark.django_db
def test_sets_full_price(new_stock_purchase, full_price):
    assert new_stock_purchase.full_price == full_price


@pytest.mark.django_db
def test_sets_discount_percentage(new_stock_purchase, discount_percentage):
    assert new_stock_purchase.discount_percentage == discount_percentage


@pytest.mark.django_db
def test_sets_quantity(new_stock_purchase, quantity):
    assert new_stock_purchase.quantity == quantity


@pytest.mark.django_db
def test_sets_cancelled(new_stock_purchase):
    assert new_stock_purchase.cancelled is False


@pytest.mark.django_db
def test_discount_percentage_can_be_100(
    to_pay,
    purchase_user,
    created_by,
    product_id,
    product_sku,
    product_name,
    full_price,
    quantity,
):
    stock_purchase = models.StockPurchase(
        user=purchase_user,
        created_by=created_by,
        to_pay=to_pay,
        product_id=product_id,
        product_sku=product_sku,
        product_name=product_name,
        full_price=full_price,
        discount_percentage=100,
        quantity=quantity,
    )
    stock_purchase.full_clean()
    stock_purchase.save()
    assert stock_purchase.discount_percentage == 100


@pytest.mark.django_db
def test_discount_percentage_cannot_be_greater_than_100(
    to_pay,
    purchase_user,
    created_by,
    product_id,
    product_sku,
    product_name,
    full_price,
    quantity,
):
    stock_purchase = models.StockPurchase(
        user=purchase_user,
        created_by=created_by,
        to_pay=to_pay,
        product_id=product_id,
        product_sku=product_sku,
        product_name=product_name,
        full_price=full_price,
        discount_percentage=101,
        quantity=quantity,
    )
    with pytest.raises(ValidationError):
        stock_purchase.full_clean()
