from unittest import mock

import pytest
from django.urls import reverse

from inventory import forms
from inventory.views import ProductSearchView


@pytest.fixture
def url(product_range):
    return reverse("inventory:product_search")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def mock_form():
    mock_form = mock.MagicMock()
    mock_form.is_valid = mock.Mock(return_value=True)
    return mock_form


@pytest.fixture
def mock_form_class(mock_form):
    with mock.patch(
        "inventory.views.views.ProductSearchView.get_form_class",
    ) as mock_get_form_class:
        mock_form_class = mock.Mock()
        mock_form_class.return_value = mock_form
        mock_get_form_class.return_value = mock_form_class
        yield mock_form_class


@pytest.fixture
def post_data():
    return {"one": 1}


@pytest.fixture
def post_response(post_data, group_logged_in_client, url):
    return group_logged_in_client.post(url, post_data)


@pytest.fixture
def initial():
    return ProductSearchView().get_initial()


@pytest.mark.django_db
def test_uses_template_for_get_request(get_response):
    assert "inventory/product_search/search_page.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_uses_template_for_post_request(post_response):
    assert "inventory/product_search/search_page.html" in (
        t.name for t in post_response.templates
    )


@pytest.mark.django_db
def test_product_ranges_in_context(
    mock_form_class, mock_form, product_range, post_response
):
    assert post_response.context["product_ranges"] == mock_form.ranges


@pytest.mark.django_db
def test_form_in_get_context(get_response):
    form = get_response.context["form"]
    assert isinstance(form, forms.ProductSearchForm)


@pytest.mark.django_db
def test_form_in_post_context(post_response):
    form = post_response.context["form"]
    assert isinstance(form, forms.ProductSearchForm)


@pytest.mark.django_db
def test_form_is_saved(mock_form_class, mock_form, post_response):
    mock_form.save.assert_called_once_with()


@pytest.mark.django_db
def test_returns_get_response_for_invaild_post(post_response):
    assert post_response.status_code == 200
    assert "inventory/product_search/search_page.html" in (
        t.name for t in post_response.templates
    )


def test_get_initial_adds_end_of_line(initial):
    assert initial["end_of_line"] == "exclude_eol"


def test_get_initial_adds_show_hidden(initial):
    assert initial["show_hidden"] is False
