import os
import tempfile
from datetime import datetime
from unittest.mock import patch

import pytest
from django.test import override_settings
from django.utils import timezone

from fnac import models


@pytest.fixture
def mock_now():
    with patch("fnac.models.offer_update.timezone.now") as mock_now:
        mock_now.return_value = timezone.make_aware(datetime(2020, 3, 10))
        yield mock_now


@pytest.fixture
def create_offer_update_export_error():
    with patch(
        "fnac.models.offer_update.create_offer_update_export"
    ) as mock_create_offer_update_export:
        mock_create_offer_update_export.side_effect = Exception()
        yield mock_create_offer_update_export


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_create_offer_update_export(mock_now):
    models.OfferUpdate.objects.create_export()
    assert models.OfferUpdate.objects.count() == 1
    export_object = models.OfferUpdate.objects.get()
    assert export_object.status == export_object.COMPLETE
    assert (
        os.path.basename(export_object.export.file.name)
        == models.OfferUpdate.objects.get_filename()
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_create_offer_update_export_error(create_offer_update_export_error):
    with pytest.raises(Exception):
        models.OfferUpdate.objects.create_export()
    assert models.OfferUpdate.objects.count() == 1
    export_object = models.OfferUpdate.objects.get()
    assert export_object.status == export_object.ERROR
    assert bool(export_object.export) is False


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_create_offer_update_export_when_one_is_in_progress(offer_update_factory,):
    offer_update_factory.create(status=models.OfferUpdate.IN_PROGRESS)
    with pytest.raises(models.OfferUpdate.AlreadyInProgress):
        models.OfferUpdate.objects.create_export()


def test_filename(mock_now):
    assert (
        models.OfferUpdate.objects.get_filename() == "fnac_offer_update_2020-03-10.csv"
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_is_in_progress(offer_update_factory,):
    assert models.OfferUpdate.objects.is_in_progress() is False
    offer_update_factory.create(status=models.OfferUpdate.IN_PROGRESS)
    assert models.OfferUpdate.objects.is_in_progress() is True
