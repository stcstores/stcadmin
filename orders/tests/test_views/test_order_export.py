from unittest.mock import patch

import pytest


@pytest.fixture
def url():
    return "/orders/export_orders/"


@pytest.fixture
def mock_create_order_export():
    with patch(
        "orders.views.models.OrderExportDownload.objects.create_download"
    ) as mock:
        yield mock


def test_logged_in_get(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url)
    assert response.status_code == 405


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


def test_logged_in_group_post(mock_create_order_export, group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 200


def test_invalid_form(url, group_logged_in_client):
    response = group_logged_in_client.post(url, {"country": 999999})
    assert response.status_code == 404


def test_export_created(url, group_logged_in_client, mock_create_order_export):
    group_logged_in_client.post(url)
    mock_create_order_export.assert_called_once()
