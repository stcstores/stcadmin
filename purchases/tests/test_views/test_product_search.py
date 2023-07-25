import pytest
from django.urls import reverse

from purchases.forms import ProductSearchForm


@pytest.fixture
def url():
    return reverse("purchases:product_search")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "purchases/product_search.html" in (t.name for t in get_response.templates)


@pytest.mark.django_db
def test_form_in_context(get_response):
    form = get_response.context["form"]
    assert isinstance(form, ProductSearchForm)
