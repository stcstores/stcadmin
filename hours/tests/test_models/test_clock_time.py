import datetime as dt
from unittest import mock

import pytest
from django.utils import timezone

from hours import models


@pytest.fixture
def user(staff_factory):
    return staff_factory.create()


@pytest.fixture
def timestamp():
    return timezone.make_aware(
        dt.datetime(
            year=2020, month=10, day=20, hour=10, minute=20, second=40, microsecond=20
        )
    )


@pytest.fixture
def mock_now(timestamp):
    with mock.patch("hours.models.timezone.now") as mock_now:
        mock_now.return_value = timestamp
        yield mock_now


@pytest.fixture
def clock_time(user, timestamp, clock_time_factory):
    return clock_time_factory.create(user=user, timestamp=timestamp)


# Test Methods


@pytest.mark.django_db
def test_str_method(timestamp, clock_time_factory):
    clock_time = clock_time_factory.create(
        user__first_name="John", user__second_name="Doe", timestamp=timestamp
    )
    assert str(clock_time) == "Clock John Doe at " + str(timestamp)


@pytest.mark.django_db
def test_direction_method_with_no_previous(clock_time):
    assert clock_time.direction() == clock_time.IN


@pytest.mark.django_db
def test_direction_method_with_previous(
    clock_time, user, timestamp, clock_time_factory
):
    clock_time_factory.create(user=user, timestamp=timestamp - dt.timedelta(hours=1))
    assert clock_time.direction() == clock_time.OUT


# Test Manager Methods


@pytest.mark.django_db
def test_clock_method(mock_now, user):
    obj = models.ClockTime.objects.clock(user=user)
    assert obj.user == user
    assert obj.timestamp == mock_now.return_value


@pytest.mark.django_db
def test_clock_method_raises_when_clocking_within_a_minute(
    mock_now, user, clock_time_factory
):
    clock_time_factory.create(
        user=user,
        timestamp=mock_now.return_value - dt.timedelta(seconds=5),
    )
    with pytest.raises(models.ClockTime.ClockedTooSoonError):
        models.ClockTime.objects.clock(user=user)
