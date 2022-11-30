import pytest


@pytest.fixture
def user(user_factory):
    return user_factory.create()


@pytest.fixture
def logged_out_client(client):
    return client


@pytest.fixture
def valid_client(client, user):
    client.login(username=user.username, password="Password")
    return client
