import pytest
from django.contrib.auth.models import Group


@pytest.fixture()
def group_name():
    return "labelmaker"


@pytest.fixture
def user(user_factory):
    return user_factory.create()


@pytest.fixture
def group(group_name):
    return Group.objects.get(name=group_name)


@pytest.fixture
def logged_out_client(client):
    return client


@pytest.fixture
def client_not_in_group(client, user):
    client.login(username=user.username, password="Password")
    return client


@pytest.fixture
def valid_client(client, group, user):
    group.user_set.add(user)
    client.login(username=user.username, password="Password")
    return client
