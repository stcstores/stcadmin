import json

import pytest
from django.urls import reverse


@pytest.fixture
def path():
    return "labelmaker:generate_product_labels"


@pytest.fixture
def size_chart_sizes(size_chart, size_chart_size_factory):
    return [
        size_chart_size_factory.create(size_chart=size_chart),
        size_chart_size_factory.create(size_chart=size_chart),
        size_chart_size_factory.create(size_chart=size_chart, name=None),
    ]


@pytest.fixture
def size_chart(size_chart_factory):
    return size_chart_factory.create()


@pytest.fixture
def url(path, size_chart, size_chart_sizes):
    return reverse(path, args=[size_chart.id])


@pytest.fixture
def page_text(valid_client, url):
    response = valid_client.get(url)
    return response.content.decode("utf8")


@pytest.fixture
def post_data(size_chart_sizes):
    return {
        "product_code": "TV001",
        "data": json.dumps(
            [
                {"size": size.id, "colour": "Green", "quantity": "1"}
                for size in size_chart_sizes
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
