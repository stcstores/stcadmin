import pytest

from orders import models


@pytest.fixture
def refund(refund_factory):
    return refund_factory.create()


@pytest.fixture
def product(product_sale_factory, refund):
    return product_sale_factory.create(order=refund.order)


@pytest.fixture
def new_product_refund(refund, product):
    product_refund = models.ProductRefund(refund=refund, product=product)
    product_refund.save()
    product_refund.refresh_from_db()
    return product_refund


@pytest.mark.django_db
def test_sets_refund(new_product_refund, refund):
    assert new_product_refund.refund == refund


@pytest.mark.django_db
def test_sets_product(new_product_refund, product):
    assert new_product_refund.product == product


@pytest.mark.django_db
def test_default_quantity(new_product_refund):
    assert new_product_refund.quantity == 1
