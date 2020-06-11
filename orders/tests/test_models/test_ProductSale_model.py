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
def sku():
    return '"ABC-213-JKE'


@pytest.fixture
def name():
    return "Test Product - Small - Red"


@pytest.fixture
def weight():
    return 235


@pytest.fixture
def quantity():
    return 3


@pytest.fixture
def price():
    return 550


@pytest.fixture
def new_product_sale(order, product_ID, sku, name, weight, quantity, price):
    sale = models.ProductSale(
        order=order,
        product_ID=product_ID,
        sku=sku,
        name=name,
        weight=weight,
        quantity=quantity,
        price=price,
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
def test_sets_sku(new_product_sale, sku):
    assert new_product_sale.sku == sku


@pytest.mark.django_db
def test_sku_defaults_null(order, product_ID, name, weight, quantity, price):
    sale = models.ProductSale(
        order=order,
        product_ID=product_ID,
        name=name,
        weight=weight,
        quantity=quantity,
        price=price,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.sku is None


@pytest.mark.django_db
def test_sets_name(new_product_sale, name):
    assert new_product_sale.name == name


@pytest.mark.django_db
def test_name_defaults_null(order, product_ID, sku, weight, quantity, price):
    sale = models.ProductSale(
        order=order,
        product_ID=product_ID,
        sku=sku,
        weight=weight,
        quantity=quantity,
        price=price,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.name is None


@pytest.mark.django_db
def test_weight_defaults_null(order, product_ID, sku, name, quantity, price):
    sale = models.ProductSale(
        order=order,
        product_ID=product_ID,
        sku=sku,
        name=name,
        quantity=quantity,
        price=price,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.weight is None


@pytest.mark.django_db
def test_sets_weight(new_product_sale, weight):
    assert new_product_sale.weight == weight


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
