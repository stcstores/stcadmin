"""Factories for the Purchases app."""

import datetime as dt

import factory
from factory.django import DjangoModelFactory

from home.factories import StaffFactory
from hours import models


class HoursSettingsFactory(DjangoModelFactory):
    class Meta:
        model = models.HoursSettings

    send_report_to = factory.Faker("ascii_email")


class HoursExportFactory(DjangoModelFactory):
    class Meta:
        model = models.HoursExport

    export_date = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    report_sent = False


class ClockTimeFactory(DjangoModelFactory):
    class Meta:
        model = models.ClockTime

    user = factory.SubFactory(StaffFactory)
    timestamp = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
