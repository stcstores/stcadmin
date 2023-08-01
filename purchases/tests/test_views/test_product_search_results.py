import pytest
from django.core.paginator import Page
from django.db.models.query import QuerySet
from django.urls import reverse


@pytest.fixture
def url():
    return reverse("purchases:product_search_results")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url, {"search_term": "search_text"})


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "purchases/product_search_results.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_products_in_context(get_response):
    products = get_response.context["object_list"]
    assert isinstance(products, QuerySet)


@pytest.mark.django_db
def test_page_obj_in_context(get_response):
    page_obj = get_response.context["page_obj"]
    assert isinstance(page_obj, Page)
