import pytest
from django.urls import reverse


@pytest.fixture
def url():
    return reverse("restock:restock")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "restock/restock.html" in [t.name for t in get_response.templates]
