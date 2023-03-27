from unittest import mock

import pytest
from django.urls import reverse

from inventory import forms


@pytest.fixture
def url():
    return reverse("inventory:start_new_product")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def created_product_id():
    return 512


@pytest.fixture
def mock_form(created_product_id):
    with mock.patch(
        "inventory.views.product_editor.StartNewProduct.get_form_class",
    ) as mock_get_form_class:
        mock_form = mock.Mock()
        mock_form.is_valid = mock.Mock(return_value=True)
        mock_form.save = mock.Mock(return_value=mock.Mock(pk=created_product_id))
        mock_get_form_class.return_value.return_value = mock_form
        yield mock_form


@pytest.fixture
def post_response(post_data, group_logged_in_client, url):
    return group_logged_in_client.post(url, post_data)


@pytest.fixture
def mock_new_range_sku():
    with mock.patch(
        "inventory.views.product_editor.models.new_range_sku"
    ) as mock_new_range_sku:
        yield mock_new_range_sku


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/product_editor/range_form.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_form_in_context(product, get_response):
    assert isinstance(get_response.context["form"], forms.CreateRangeForm)


@pytest.mark.django_db
def test_managed_by_added_to_form_initial(user, get_response):
    initial = get_response.context["form"].initial
    assert initial["managed_by"] == user


@pytest.mark.django_db
def test_sku_added_to_form_initial(mock_new_range_sku, get_response):
    initial = get_response.context["form"].initial
    assert initial["sku"] == mock_new_range_sku.return_value


@pytest.mark.django_db
def test_form_is_saved(mock_form, group_logged_in_client, url):
    group_logged_in_client.post(url, {})
    mock_form.save.assert_called_once_with()


@pytest.mark.django_db
def test_success_redirect(created_product_id, mock_form, group_logged_in_client, url):
    response = group_logged_in_client.post(url, {})
    assert response.status_code == 302
    assert response["location"] == reverse(
        "inventory:create_initial_variation",
        kwargs={"range_pk": created_product_id},
    )
