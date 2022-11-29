import pytest


@pytest.fixture
def logged_out_client(client):
    return client


@pytest.fixture
def valid_client(client, user):
    client.login(username=user.username, password="Password")
    return client
