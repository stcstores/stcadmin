import pytest
from django.urls import reverse


@pytest.fixture
def supplier(supplier_factory):
    return supplier_factory.create(active=True, blacklisted=True)


@pytest.fixture
def url(supplier):
    return reverse("inventory:blacklist_supplier", kwargs={"pk": supplier.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_supplier_set_inactive(supplier, get_response):
    supplier.refresh_from_db()
    assert supplier.active is False


@pytest.mark.django_db
def test_supplier_set_not_blacklisted(supplier, get_response):
    supplier.refresh_from_db()
    assert supplier.blacklisted is True


@pytest.mark.django_db
def test_redirect_url(supplier, get_response):
    assert get_response["location"] == supplier.get_absolute_url()
