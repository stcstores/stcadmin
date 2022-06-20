import pytest

from home.models import Staff


@pytest.fixture
def stcadmin_user(user_factory):
    return user_factory.create()


@pytest.fixture
def first_name():
    return "Test"


@pytest.fixture
def second_name():
    return "User"


@pytest.fixture
def email_address():
    return "test@testing.co.uk"


@pytest.fixture
def new_staff(stcadmin_user, first_name, second_name, email_address):
    new_staff = Staff(
        stcadmin_user=stcadmin_user,
        first_name=first_name,
        second_name=second_name,
        email_address=email_address,
    )
    new_staff.save()
    return new_staff


@pytest.fixture
def hidden_staff(staff_factory):
    return staff_factory.create(hidden=True)


@pytest.fixture
def unhidden_staff(staff_factory):
    return staff_factory.create(hidden=False)


@pytest.mark.django_db
def test_staff_has_stcadmin_user(stcadmin_user, new_staff):
    assert new_staff.stcadmin_user == stcadmin_user


@pytest.mark.django_db
def test_staff_has_first_name(first_name, new_staff):
    assert new_staff.first_name == first_name


@pytest.mark.django_db
def test_staff_has_second_name(second_name, new_staff):
    assert new_staff.second_name == second_name


@pytest.mark.django_db
def test_staff_has_email_address(email_address, new_staff):
    assert new_staff.email_address == email_address


@pytest.mark.django_db
def test_staff_hiden_attribute_defaults_to_false(new_staff):
    assert new_staff.hidden is False


@pytest.mark.django_db
def test_staff_email_address_attribute_defaults_to_none(
    stcadmin_user, first_name, second_name
):
    new_staff = Staff(
        stcadmin_user=stcadmin_user,
        first_name=first_name,
        second_name=second_name,
    )
    new_staff.save()
    assert new_staff.email_address is None


@pytest.mark.django_db
def test_staff_unhidden_manger_returns_unhidden_staff(unhidden_staff):
    assert unhidden_staff in Staff.unhidden.all()


@pytest.mark.django_db
def test_staff_unhidden_manger_does_not_return_hidden_staff(hidden_staff):
    assert hidden_staff not in Staff.unhidden.all()


@pytest.mark.django_db
def test_staff_str_method(first_name, second_name, new_staff):
    assert str(new_staff) == f"{first_name} {second_name}"


@pytest.mark.django_db
def test_staff_full_name_method(first_name, second_name, new_staff):
    assert new_staff.full_name() == f"{first_name} {second_name}"
