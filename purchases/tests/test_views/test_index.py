import pytest
from django.urls import reverse


@pytest.fixture
def url():
    return reverse("purchases:index")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "purchases/index.html" in [t.name for t in get_response.templates]


@pytest.mark.django_db
def test_status_code(get_response):
    assert get_response.status_code == 200
