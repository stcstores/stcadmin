from unittest.mock import patch

from itd import tasks


@patch("itd.models.ITDManifestManager.close_manifest")
def test_close_manifest_task(mock_close_manifest, celery_app, celery_worker):
    tasks.close_manifest.delay(5).get(timeout=10)
    mock_close_manifest.assert_called_once_with(5)
