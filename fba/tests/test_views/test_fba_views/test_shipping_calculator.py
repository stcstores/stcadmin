import pytest
from django.urls import reverse

from fba.views.fba import ShippingCalculator


def test_template_name_attribute():
    assert ShippingCalculator.template_name == "fba/shipping_calculator.html"


@pytest.fixture
def active_region(fba_region_factory):
    return fba_region_factory.create(active=True)


@pytest.fixture
def inactive_region(fba_region_factory):
    return fba_region_factory.create(active=False)


@pytest.fixture
def url():
    return reverse("fba:shipping_calculator")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(get_response):
    assert "fba/shipping_calculator.html" in (t.name for t in get_response.templates)


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.mark.django_db
def test_active_region_in_context(active_region, get_response):
    assert get_response.context["regions"].contains(active_region)


@pytest.mark.django_db
def test_inactive_region_in_context(active_region, inactive_region, get_response):
    assert get_response.context["regions"].contains(inactive_region) is False
