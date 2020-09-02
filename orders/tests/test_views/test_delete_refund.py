import pytest

from orders import models


@pytest.fixture
def refund(refund_factory):
    return refund_factory.create()


@pytest.fixture
def url(refund):
    def _url(refund_pk=None):
        if refund_pk is None:
            refund_pk = refund.pk
        return f"/orders/refund/{refund_pk}/delete_refund/"

    return _url


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url())


@pytest.fixture
def valid_get_response_content(url, valid_get_request):
    return valid_get_request(url()).content.decode("utf8")


@pytest.mark.django_db
def test_logged_in_get(url, logged_in_client):
    response = logged_in_client.get(url())
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_out_get(client, url):
    response = client.get(url())
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url())
    assert response.status_code == 200


@pytest.mark.django_db
def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url())
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_out_post(client, url):
    response = client.post(url())
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url())
    assert response.status_code == 405


@pytest.mark.django_db
def test_delete_refund(refund, group_logged_in_client, url):
    group_logged_in_client.get(url(refund.id))
    assert models.Refund.objects.filter(id=refund.id).exists() is False


@pytest.mark.django_db
def test_delete_non_existant_refund(group_logged_in_client, url):
    response = group_logged_in_client.get(url(9999999999))
    assert response.status_code == 404
