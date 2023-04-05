from unittest import mock

import pytest
from django.urls import reverse

from inventory import models


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create(status=models.ProductRange.CREATING)


@pytest.fixture
def url(product_range):
    return reverse(
        "inventory:complete_new_product", kwargs={"range_pk": product_range.pk}
    )


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_calls_complete_new_range(user, url, product_range, group_logged_in_client):
    with mock.patch(
        "inventory.views.product_editor.get_object_or_404"
    ) as mock_get_object:
        mock_get_object.return_value.get_absolute_url.return_value = ""
        group_logged_in_client.get(url)
        mock_get_object.return_value.complete_new_range.assert_called_once_with(user)


@pytest.mark.django_db
def test_redirect(get_response, product_range):
    assert get_response.status_code == 302
    assert get_response["location"] == product_range.get_absolute_url()
