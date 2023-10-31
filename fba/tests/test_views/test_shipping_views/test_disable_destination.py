import pytest
from django.urls import reverse


@pytest.fixture
def destination(fba_shipment_destination_factory):
    return fba_shipment_destination_factory.create(is_enabled=True)


@pytest.fixture
def url(destination):
    return reverse("fba:remove_destination", args=[destination.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_redirects(get_response):
    assert get_response.status_code == 302
    assert get_response["Location"] == reverse("fba:shipment_destinations")


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.mark.django_db
def test_disables_destination(destination, get_response):
    destination.refresh_from_db()
    assert destination.is_enabled is False
