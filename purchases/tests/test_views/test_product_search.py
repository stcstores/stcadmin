import pytest
from django.core.paginator import Page
from django.db.models.query import QuerySet
from django.urls import reverse

from purchases.forms import ProductSearchForm


@pytest.fixture
def url():
    return reverse("purchases:product_search")


@pytest.fixture
def product(product_factory):
    return product_factory.create(product_range__name="text")


@pytest.fixture
def form_data():
    return {"search_term": "text"}


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def get_response_with_search(group_logged_in_client, url, form_data):
    return group_logged_in_client.get(url, form_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "purchases/product_search.html" in [t.name for t in get_response.templates]


@pytest.mark.django_db
def test_form_in_context(get_response):
    form = get_response.context["form"]
    assert isinstance(form, ProductSearchForm)


@pytest.mark.django_db
def test_products_in_context(get_response_with_search):
    products = get_response_with_search.context["object_list"]
    assert isinstance(products, QuerySet)


@pytest.mark.django_db
def test_returns_product(product, get_response_with_search):
    assert product in get_response_with_search.context["object_list"]


@pytest.mark.django_db
def test_page_obj_in_context(get_response_with_search):
    page_obj = get_response_with_search.context["page_obj"]
    assert isinstance(page_obj, Page)
