import pytest
from django.shortcuts import reverse
from pytest_django.asserts import assertTemplateUsed

from orders import models


@pytest.fixture
def breakage(breakage_factory):
    return breakage_factory.create()


@pytest.fixture
def url(breakage):
    return f"/orders/delete_breakage/{breakage.id}/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


@pytest.mark.django_db
def test_logged_in_get(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(valid_get_response, "orders/breakage_confirm_delete.html")
        is not False
    )


@pytest.mark.django_db
def test_breakage_is_not_deleted_for_get_request(valid_get_response, breakage):
    assert models.Breakage.objects.filter(id=breakage.id).exists() is True


@pytest.mark.django_db
def test_breakage_is_deleted_for_post_request(group_logged_in_client, url, breakage):
    group_logged_in_client.post(url)
    assert models.Breakage.objects.filter(id=breakage.id).exists() is False


@pytest.mark.django_db
def test_redirects(group_logged_in_client, url, breakage):
    response = group_logged_in_client.post(url)
    assert response.url == reverse("orders:breakages")
