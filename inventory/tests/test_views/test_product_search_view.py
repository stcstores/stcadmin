import pytest
from django.urls import reverse

from inventory import forms
from inventory.views import ProductSearchView


@pytest.fixture
def url(product_range):
    return reverse("inventory:product_search")


@pytest.fixture
def params():
    return {"one": 1}


@pytest.fixture
def get_response(params, group_logged_in_client, url):
    return group_logged_in_client.get(url, params)


@pytest.fixture
def initial():
    return ProductSearchView().get_initial()


@pytest.mark.django_db
def test_uses_template_for_get_request(get_response):
    assert "inventory/product_search/search_page.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_uses_template_for_post_request(get_response):
    assert "inventory/product_search/search_page.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_form_in_get_context(get_response):
    form = get_response.context["form"]
    assert isinstance(form, forms.ProductSearchForm)


@pytest.mark.django_db
def test_returns_get_response_for_invaild_post(get_response):
    assert get_response.status_code == 200
    assert "inventory/product_search/search_page.html" in [
        t.name for t in get_response.templates
    ]


def test_get_initial_adds_end_of_line(initial):
    assert initial["archived"] == "exclude_archived"
