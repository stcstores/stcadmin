import json

import pytest
from django.urls import reverse


@pytest.fixture
def path():
    return "labelmaker:generate_product_labels"


@pytest.fixture
def url(path):
    return reverse(path)


@pytest.fixture
def post_data():
    return {
        "product_code": [f"TV00{i}" for i in range(4)],
        "data": json.dumps(
            [
                {"size": "UK 5", "colour": "Green", "quantity": "1"},
                {"size": "UK 5", "colour": "Red", "quantity": "1"},
                {"size": "UK 6", "colour": "Green", "quantity": "1"},
                {"size": "UK 6", "colour": "Red", "quantity": "1"},
            ]
        ),
    }


@pytest.mark.django_db
def test_cannot_access_logged_out(logged_out_client, url):
    assert logged_out_client.get(url).status_code == 302


@pytest.mark.django_db
def test_cannot_access_if_not_in_group(client_not_in_group, url):
    assert client_not_in_group.get(url).status_code == 403


@pytest.mark.django_db
def test_cannot_get(valid_client, url):
    assert valid_client.get(url).status_code == 405


@pytest.mark.django_db
def test_returns_pdf(valid_client, url, post_data):
    response = valid_client.post(url, post_data)
    assert response["Content-Type"] == "application/pdf"


@pytest.mark.django_db
def test_response_filename(valid_client, url, post_data):
    response = valid_client.post(url, post_data)
    assert response["Content-Disposition"] == 'filename="labels.pdf"'
