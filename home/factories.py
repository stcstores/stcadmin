"""Model factories for the home app."""


import datetime as dt

import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.timezone import make_aware
from factory import fuzzy
from factory.django import DjangoModelFactory

from home import models


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group

    name = fuzzy.FuzzyText()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Faker("user_name")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "Password")
    email = factory.Faker("email")
    is_staff = False
    is_active = True
    is_superuser = False
    last_login = fuzzy.FuzzyDateTime(make_aware(dt.datetime(2008, 1, 1)))
    date_joined = fuzzy.FuzzyDateTime(make_aware(dt.datetime(2008, 1, 1)))


class StaffFactory(DjangoModelFactory):
    class Meta:
        model = models.Staff

    stcadmin_user = factory.RelatedFactory(UserFactory)
    first_name = factory.Faker("first_name")
    second_name = factory.Faker("last_name")
    email_address = factory.Faker("email")
    hidden = False
