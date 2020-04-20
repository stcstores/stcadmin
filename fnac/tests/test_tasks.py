from unittest.mock import patch

from fnac import tasks


@patch("fnac.tasks.models.MissingInformationExport")
def test_create_missing_information_export_task(
    mock_MissingInformation_export, celery_app, celery_worker,
):
    tasks.create_missing_information_export.delay().get(timeout=10)
    mock_MissingInformation_export.objects.create_export.assert_called_once()
