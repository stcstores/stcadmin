import pytest
from django.urls import reverse


@pytest.fixture
def token():
    return "suodghoi4h0298h309hg08h30h0st"


@pytest.fixture
def shipment_config(shipment_config_factory, token):
    return shipment_config_factory.create(token=token)


@pytest.fixture
def export(fba_shipment_export_factory):
    return fba_shipment_export_factory.create()


@pytest.fixture
def form_data(token, export):
    return {"token": token, "export_id": export.pk}


@pytest.fixture
def url():
    return reverse("fba:api_download_address_file")


@pytest.fixture
def post_response(shipment_config, group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_request_from_user_not_in_group(shipment_config, url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_request_without_token(shipment_config, url, group_logged_in_client):
    response = group_logged_in_client.post(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_request_with_incorrect_token(shipment_config, url, group_logged_in_client):
    response = group_logged_in_client.post(url, {"token": "ihosdhfios"})
    assert response.status_code == 401


@pytest.mark.django_db
def test_filename(post_response):
    assert (
        post_response.headers["Content-Disposition"]
        == "attachment; filename=FBA_Shipment_ADDRESS.csv"
    )


@pytest.mark.django_db
def test_content(export, post_response):
    assert post_response.content == export.generate_address_file().encode("utf8")
