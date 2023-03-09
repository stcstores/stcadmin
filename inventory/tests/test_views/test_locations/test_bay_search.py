import pytest
from django.urls import reverse

from inventory import forms
from inventory.views.locations import BaySearch


@pytest.fixture
def bay(bay_factory):
    return bay_factory.create()


@pytest.fixture
def url():
    return reverse("inventory:bay_search")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def get_response_with_bay(bay, group_logged_in_client, url):
    return group_logged_in_client.get(url, {"bay": bay.id})


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/bay_search.html" in (t.name for t in get_response.templates)


@pytest.mark.django_db
def test_form_in_context_for_empty_request(get_response):
    assert isinstance(get_response.context["form"], forms.BaySearchForm)


@pytest.mark.django_db
def test_form_in_context(get_response_with_bay):
    assert isinstance(get_response_with_bay.context["form"], forms.BaySearchForm)


@pytest.mark.django_db
def test_products_in_context(
    group_logged_in_client,
    url,
    bay,
    bay_factory,
    product_factory,
    product_bay_link_factory,
):
    product = product_factory.create()
    other_bay = bay_factory.create()
    product_bay_link_factory.create(product=product, bay=bay)
    product_bay_link_factory.create(product=product, bay=other_bay)
    response = group_logged_in_client.get(url, {"bay": bay.id})
    assert response.context["products"] == [(product, [other_bay])]


@pytest.mark.django_db
def test_get_other_bays(bay, bay_factory, product_factory, product_bay_link_factory):
    product = product_factory.create()
    other_bay = bay_factory.create()
    product_bay_link_factory.create(product=product, bay=bay)
    product_bay_link_factory.create(product=product, bay=other_bay)
    returned_value = BaySearch().get_other_bays(product, bay)
    assert returned_value == [other_bay]
