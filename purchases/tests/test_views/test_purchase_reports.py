import pytest
from django.core.paginator import Page
from django.db.models.query import QuerySet
from django.urls import reverse


@pytest.fixture
def purchase_exports(purchase_export_factory):
    return purchase_export_factory.create_batch(3)


@pytest.fixture
def url(purchase_exports):
    return reverse("purchases:purchase_reports")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "purchases/purchase_reports.html" in (t.name for t in get_response.templates)


@pytest.mark.django_db
def test_exports_in_context(get_response):
    purchase_exports = get_response.context["object_list"]
    assert isinstance(purchase_exports, QuerySet)


@pytest.mark.django_db
def test_page_obj_in_context(get_response):
    page_obj = get_response.context["page_obj"]
    assert isinstance(page_obj, Page)


@pytest.mark.django_db
def test_object_list_contains_exports(purchase_exports, get_response):
    for purchase_export in purchase_exports:
        assert purchase_export in get_response.context["object_list"]
