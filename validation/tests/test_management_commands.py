from unittest.mock import patch

from stcadmin.tests.stcadmin_test import STCAdminTest
from validation.management import commands


class TestValidateModels(STCAdminTest):
    @patch("validation.management.commands.validate_models.RunModelValidation")
    def test_validate_models(self, mock_RunModelValidation):
        commands.validate_models.Command().handle()
        mock_RunModelValidation.run.assert_called_once()

    @patch("validation.management.commands.validate_models.RunModelValidation")
    def test_validate_models_with_error(self, mock_RunModelValidation):
        mock_RunModelValidation.run.side_effect = Exception
        with self.assertRaises(Exception):
            commands.validate_models.Command().handle()
        mock_RunModelValidation.run.assert_called_once()
