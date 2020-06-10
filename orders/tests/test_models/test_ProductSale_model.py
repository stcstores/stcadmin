import pytest
from django.db import IntegrityError

from orders import models


@pytest.fixture
def order(order_factory):
    return order_factory.create()


@pytest.fixture
def product_ID():
    return "484894684"


@pytest.fixture
def quantity():
    return 3


@pytest.fixture
def price():
    return 550


@pytest.fixture
def new_product_sale(order, product_ID, quantity, price):
    sale = models.ProductSale(
        order=order, product_ID=product_ID, quantity=quantity, price=price
    )
    sale.save()
    return sale


@pytest.mark.django_db
def test_sets_order(new_product_sale, order):
    assert new_product_sale.order == order


@pytest.mark.django_db
def test_sets_product_ID(new_product_sale, product_ID):
    assert new_product_sale.product_ID == product_ID


@pytest.mark.django_db
def test_sets_quantity(new_product_sale, quantity):
    assert new_product_sale.quantity == quantity


@pytest.mark.django_db
def test_sets_price(new_product_sale, price):
    assert new_product_sale.price == price


@pytest.mark.django_db
def test_order_and_product_ID_are_unique_together(
    order, product_ID, product_sale_factory
):
    product_sale_factory.create(order=order, product_ID=product_ID)
    with pytest.raises(IntegrityError):
        product_sale_factory.create(order=order, product_ID=product_ID)
