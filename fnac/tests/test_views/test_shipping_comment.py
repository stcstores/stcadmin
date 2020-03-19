import pytest

from fnac import models


@pytest.fixture
def url():
    return "/fnac/shipping_comment/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def post_data(comment_text):
    return {"comment": comment_text}


@pytest.fixture
def valid_post_response(comment_factory, valid_post_request, url, post_data):
    comment_factory.create()
    return valid_post_request(url, post_data)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


@pytest.fixture
def comment_text():
    return "Shipping Information\nShips in 5 days"


@pytest.fixture
def comment(comment_text):
    return models.Comment.objects.set_comment_text(comment_text)


def test_logged_out_get_method(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(valid_get_response):
    assert valid_get_response.status_code == 200


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


def test_logged_in_group_post(valid_post_response):
    assert valid_post_response.status_code == 302


@pytest.mark.django_db
def test_current_comment_is_displayed(
    comment, comment_text, valid_get_response_content
):
    assert comment_text in valid_get_response_content


@pytest.mark.django_db
def test_comment_is_updated(comment, comment_text, valid_post_response):
    assert models.Comment.objects.get_comment_text() == comment_text
