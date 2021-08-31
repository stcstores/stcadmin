import uuid

import pytest
from django.contrib.auth.models import Group

INVENTORY_GROUP_NAME = "inventory"


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
    group, _ = Group.objects.get_or_create(name=INVENTORY_GROUP_NAME)
    group.user_set.add(user)
    client.login(username=user.username, password=test_password)
    return client


@pytest.fixture
def valid_get_request(group_logged_in_client):
    def _valid_get_request(url):
        return group_logged_in_client.get(url)

    return _valid_get_request


@pytest.fixture
def valid_post_request(group_logged_in_client):
    def _valid_post_request(*args, **kwargs):
        return group_logged_in_client.post(*args, **kwargs)

    return _valid_post_request
