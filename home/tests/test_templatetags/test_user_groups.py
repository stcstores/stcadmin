import pytest

from home.templatetags import stcadmin_extras


@pytest.fixture
def groups(group_factory):
    return group_factory.create_batch(3)


@pytest.fixture
def user(user_factory, groups):
    user = user_factory.create()
    for group in groups:
        user.groups.add(group)
    return user


@pytest.mark.django_db
def test_with_groups(user, groups):
    assert list(stcadmin_extras.user_groups(user)) == [group.name for group in groups]


@pytest.mark.django_db
def test_without_groups(user_factory):
    user = user_factory.create()
    assert len(stcadmin_extras.user_groups(user)) == 0
