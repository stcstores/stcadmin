import pytest
from django.urls import reverse

from fba import forms


@pytest.fixture
def destination(fba_shipment_destination_factory):
    return fba_shipment_destination_factory.create()


@pytest.fixture
def url():
    return reverse("fba:create_shipment_select_destination")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "fba/shipments/create_shipment/select_destination.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_status_code(get_response):
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    context = get_response.context
    assert isinstance(context["form"], forms.FBAShipmentDestinationForm)


def test_redirect(group_logged_in_client, url, destination):
    response = group_logged_in_client.post(url, {"destination": destination.id})
    assert response.status_code == 302
    assert response["Location"] == reverse("fba:create_shipment", args=[destination.pk])


def test_invalid_submission(group_logged_in_client, url):
    response = group_logged_in_client.post(url, {})
    assert response.status_code == 200
