import uuid

import pytest
from django.contrib.auth.models import Group

FNAC_GROUP_NAME = "fnac"


@pytest.fixture
def test_password():
    return "strong-test-pass"


@pytest.fixture
def create_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        kwargs["password"] = test_password
        if "username" not in kwargs:
            kwargs["username"] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def logged_in_client(client, create_user, test_password):
    user = create_user()
    client.login(username=user.username, password=test_password)
    return client


@pytest.fixture
def group_logged_in_client(client, create_user, test_password):
    user = create_user()
    group, _ = Group.objects.get_or_create(name=FNAC_GROUP_NAME)
    group.user_set.add(user)
    client.login(username=user.username, password=test_password)
    return client


@pytest.fixture
def fnac_index_url():
    return "/fnac/"


@pytest.fixture
def valid_get_request(group_logged_in_client):
    def _valid_get_request(url):
        return group_logged_in_client.get(url)

    return _valid_get_request


@pytest.fixture
def fnac_index_response(valid_get_request, fnac_index_url):
    return valid_get_request(fnac_index_url)


def test_fnac_index_logged_out_get_method(fnac_index_url, logged_in_client):
    response = logged_in_client.get(fnac_index_url)
    assert response.status_code == 403


def test_fnac_index_logged_out_get(client, fnac_index_url):
    response = client.get(fnac_index_url)
    assert response.status_code == 302


def test_fanc_index_logged_in_group_get(fnac_index_response):
    assert fnac_index_response.status_code == 200


def test_fnac_index_logged_out_post_method(fnac_index_url, logged_in_client):
    response = logged_in_client.post(fnac_index_url)
    assert response.status_code == 403


def test_fnac_index_logged_out_post(client, fnac_index_url):
    response = client.post(fnac_index_url)
    assert response.status_code == 302


def test_fanc_index_logged_in_group_post(group_logged_in_client, fnac_index_url):
    response = group_logged_in_client.post(fnac_index_url)
    assert response.status_code == 405


def test_fnac_index_header(fnac_index_response):
    assert fnac_index_response.content.decode("utf8") == "<h1>Hello</h1>"
