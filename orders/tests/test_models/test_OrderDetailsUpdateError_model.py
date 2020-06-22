import pytest

from orders import models


@pytest.fixture
def order_details_update(order_details_update_factory):
    return order_details_update_factory.create()


@pytest.fixture
def product_sale(product_sale_factory):
    return product_sale_factory.create()


@pytest.fixture
def text():
    return "Exception text"


@pytest.fixture
def new_order_details_update_error(order_details_update, product_sale, text):
    error = models.OrderDetailsUpdateError(
        update=order_details_update, product_sale=product_sale, text=text
    )
    error.save()
    error.refresh_from_db()
    return error


@pytest.mark.django_db
def test_sets_update(new_order_details_update_error, order_details_update):
    assert new_order_details_update_error.update == order_details_update


@pytest.mark.django_db
def test_sets_product_sale(new_order_details_update_error, product_sale):
    assert new_order_details_update_error.product_sale == product_sale


@pytest.mark.django_db
def test_sets_text(new_order_details_update_error, text):
    assert new_order_details_update_error.text == text
