import datetime as dt

import pytest
from django.utils.timezone import make_aware

from hardware import models


@pytest.fixture
def computer_maintainance_job(computer_maintainance_job_factory):
    return computer_maintainance_job_factory.create()


@pytest.mark.django_db
def test_full_clean(computer_maintainance_job):
    assert computer_maintainance_job.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_completed_at_attribute(computer_maintainance_job):
    assert isinstance(computer_maintainance_job.completed_at, dt.datetime)


@pytest.mark.django_db
def test_has_computer_attribute(computer_maintainance_job):
    assert isinstance(computer_maintainance_job.computer, models.Computer)


@pytest.mark.django_db
def test_has_cleaned_attribute(computer_maintainance_job):
    assert isinstance(computer_maintainance_job.cleaned, bool)


@pytest.mark.django_db
def test_has_os_reinstalled_attribute(computer_maintainance_job):
    assert isinstance(computer_maintainance_job.os_reinstalled, bool)


@pytest.mark.django_db
def test_has_notes_attribute(computer_maintainance_job):
    assert isinstance(computer_maintainance_job.notes, str)


# Test Methods


@pytest.mark.django_db
def test_str_method(computer_maintainance_job_factory):
    job = computer_maintainance_job_factory.create(
        computer__name="Joe", completed_at=make_aware(dt.datetime(2024, 2, 2))
    )
    assert str(job) == "Joe on 02 February 2024"
