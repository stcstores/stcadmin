from unittest import mock

import pytest
from django.urls import reverse

from inventory import forms


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create()


@pytest.fixture
def url(product_range):
    return reverse("inventory:edit_range_details", kwargs={"pk": product_range.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def mock_form(product_range):
    with mock.patch(
        "inventory.views.product_editor.EditRangeDetails.get_form_class",
    ) as mock_get_form_class:
        mock_form = mock.Mock()
        mock_form.is_valid = mock.Mock(return_value=True)
        mock_form.save = mock.Mock(return_value=product_range)
        mock_get_form_class.return_value.return_value = mock_form
        yield mock_form


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/product_editor/range_form.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_form_in_context(get_response):
    form = get_response.context["form"]
    assert isinstance(form, forms.EditRangeForm)


@pytest.mark.django_db
def test_form_is_saved(mock_form, group_logged_in_client, url):
    group_logged_in_client.post(url, {})
    mock_form.save.assert_called_once_with()


@pytest.mark.django_db
def test_success_redirect(mock_form, group_logged_in_client, url, product_range):
    response = group_logged_in_client.post(url, {})
    assert response.status_code == 302
    assert response["location"] == reverse(
        "inventory:edit_new_product", kwargs={"range_pk": product_range.pk}
    )
