from decimal import Decimal
from unittest import mock

import pytest
from django.urls import reverse


@pytest.fixture
def existing_purchase_price():
    return Decimal("5.30")


@pytest.fixture
def new_purchase_price():
    return Decimal("8.65")


@pytest.fixture
def product(product_factory, existing_purchase_price):
    return product_factory.create(purchase_price=existing_purchase_price)


@pytest.fixture
def url():
    return reverse("restock:update_purchase_price")


@pytest.fixture
def form_data(product, new_purchase_price):
    return {"product_id": product.id, "updated_purchase_price": new_purchase_price}


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_updates_purchase_price(product, new_purchase_price, post_response):
    product.refresh_from_db()
    assert product.purchase_price == new_purchase_price


@pytest.mark.django_db
def test_response_json(new_purchase_price, post_response):
    assert post_response.json() == {"purchase_price": str(new_purchase_price)}


@pytest.mark.django_db
def test_returns_bad_request_on_error(url, form_data, group_logged_in_client):
    with mock.patch("restock.views.get_object_or_404") as mock_get_object:
        mock_get_object.side_effect = Exception
        response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 400
