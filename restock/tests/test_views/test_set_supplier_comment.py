from unittest import mock

import pytest
from django.urls import reverse


@pytest.fixture
def new_comment():
    return "Comment Text"


@pytest.fixture
def supplier(supplier_factory):
    return supplier_factory.create()


@pytest.fixture
def url():
    return reverse("restock:set_supplier_comment")


@pytest.fixture
def form_data(supplier, new_comment):
    return {"supplier_id": supplier.id, "comment": new_comment}


@pytest.fixture
def post_response(group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_sets_comment(supplier, new_comment, post_response):
    supplier.refresh_from_db()
    assert supplier.restock_comment == new_comment


@pytest.mark.django_db
def test_response_json(new_comment, post_response):
    assert post_response.json() == {"comment": new_comment}


@pytest.mark.django_db
@mock.patch("restock.views.get_object_or_404")
def test_returns_bad_request_on_error(
    mock_get_object, url, form_data, group_logged_in_client
):
    mock_get_object.side_effect = Exception
    response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 400
