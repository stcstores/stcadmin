import uuid

import pytest
from django.contrib.auth.models import Group

INVENTORY_GROUP_NAME = "inventory"


@pytest.fixture
def test_password():
    return "strong-test-pass"


@pytest.fixture
def user(django_user_model, test_password):
    return django_user_model.objects.create_user(
        password=test_password, username=str(uuid.uuid4())
    )


@pytest.fixture
def group_logged_in_client(client, user, test_password):
    group, _ = Group.objects.get_or_create(name=INVENTORY_GROUP_NAME)
    group.user_set.add(user)
    client.login(username=user.username, password=test_password)
    return client


@pytest.fixture
def logged_in_client(client, user, test_password):
    client.login(username=user.username, password=test_password)
    return client
