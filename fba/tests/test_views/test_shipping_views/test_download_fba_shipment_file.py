import pytest
from django.urls import reverse


@pytest.fixture
def export(fba_shipment_export_factory):
    return fba_shipment_export_factory.create()


@pytest.fixture
def url(export):
    return reverse("fba:download_shipment_file", args=[export.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_response(get_response):
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.mark.django_db
def test_filename(export, get_response):
    assert (
        get_response.headers["Content-Disposition"]
        == f"attachment; filename=FBA_Shipment_File_{export.created_at.strftime('%Y-%m-%d')}.csv"
    )


@pytest.mark.django_db
def test_content(export, get_response):
    assert get_response.content == export.generate_export_file().encode("utf8")
