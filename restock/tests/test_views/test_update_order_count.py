from unittest import mock

import pytest
from django.urls import reverse


@pytest.fixture
def new_reorder_count():
    return 25


@pytest.fixture
def mock_reorder_model(new_reorder_count):
    with mock.patch("restock.views.models.Reorder") as mock_reorder_model:
        mock_reorder_model.objects.set_count.return_value = new_reorder_count
        yield mock_reorder_model


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def url():
    return reverse("restock:update_order_count")


@pytest.fixture
def form_data(product, new_reorder_count):
    return {"product_id": product.id, "updated_order_count": new_reorder_count}


@pytest.fixture
def post_response(mock_reorder_model, group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_calls_set_count(mock_reorder_model, product, new_reorder_count, post_response):
    mock_reorder_model.objects.set_count.assert_called_once_with(
        product, new_reorder_count
    )


@pytest.mark.django_db
def test_response_json(new_reorder_count, post_response):
    assert post_response.json() == {"count": new_reorder_count}


@pytest.mark.django_db
def test_returns_bad_request_on_error(url, form_data, group_logged_in_client):
    with mock.patch("restock.views.get_object_or_404") as mock_get_object:
        mock_get_object.side_effect = Exception
        response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 400
