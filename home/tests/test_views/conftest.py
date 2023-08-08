import uuid

import pytest


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
def user(create_user):
    return create_user()


@pytest.fixture
def logged_out_client(client):
    return client


@pytest.fixture
def valid_client(user, client, test_password):
    client.login(username=user.username, password=test_password)
    return client
