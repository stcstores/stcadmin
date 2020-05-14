from unittest.mock import Mock, patch

import pytest

from itd import tasks


@patch("itd.models.ITDManifestManager.close_manifest")
def test_close_manifest_task(mock_close_manifest, celery_app, celery_worker):
    tasks.close_manifest.delay(5).get(timeout=10)
    mock_close_manifest.assert_called_once_with(5)


@pytest.mark.django_db
@patch("itd.models.ITDManifest")
def test_clear_manifest_files_task(mock_ITDManifest, celery_app, celery_worker):
    manifest = Mock(id=5)
    mock_ITDManifest.objects.get.return_value = manifest
    tasks.clear_manifest_files.delay(manifest.id).get(timeout=5)
    mock_ITDManifest.objects.get.assert_called_once_with(id=manifest.id)
    manifest.clear_files.assert_called_once()
