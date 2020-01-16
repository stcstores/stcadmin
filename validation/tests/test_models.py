from datetime import datetime
from unittest.mock import Mock, patch

from django.utils.timezone import make_aware

from stcadmin.tests.stcadmin_test import STCAdminTest
from validation import models
from validation.levels import Levels


def mock_now():
    return make_aware(datetime(2020, 1, 16))


class TestModelValidationLog(STCAdminTest):
    fixtures = ("validation/model_validation_log",)

    @patch("django.utils.timezone.now", mock_now)
    def test_object_creation(self):
        app = "app"
        model = "Model"
        error_level = Levels.CRITICAL.level
        object_validator = "object name"
        validation_check = "check name"
        error_message = "There was an error"
        log = models.ModelValidationLog.objects.create(
            app=app,
            model=model,
            error_level=error_level,
            object_validator=object_validator,
            validation_check=validation_check,
            error_message=error_message,
        )
        self.assertEqual(app, log.app)
        self.assertEqual(model, log.model)
        self.assertEqual(error_level, log.error_level)
        self.assertEqual(object_validator, log.object_validator)
        self.assertEqual(validation_check, log.validation_check)
        self.assertEqual(error_message, log.error_message)
        self.assertEqual(mock_now(), log.last_seen)

    def test_str(self):
        log = models.ModelValidationLog.objects.get(id=1)
        log.app = "app"
        log.model = "Model"
        log.error_level = Levels.CRITICAL.level
        log.object_validator = "object name"
        self.assertEqual("app.Model object name: Critical", str(log))

    def test_level_method(self):
        log = models.ModelValidationLog.objects.get(id=1)
        log.error_level = Levels.CRITICAL.level
        self.assertEqual(Levels.CRITICAL, log.level())
        log.error_level = Levels.FORMATTING.level
        self.assertEqual(Levels.FORMATTING, log.level())

    def test_clear_validation_runner(self):
        app = "inventory"
        model = "Supplier"
        mock_runner = Mock(app_name=app, model_name=model)
        self.assertTrue(
            models.ModelValidationLog.objects.filter(app=app, model=model).exists()
        )
        models.ModelValidationLog.clear_validation_runner(mock_runner)
        self.assertFalse(
            models.ModelValidationLog.objects.filter(app=app, model=model).exists()
        )

    @patch("django.utils.timezone.now", mock_now)
    def test_log_failed_validation(self):
        app = "app"
        model = "Model"
        error_level = Levels.CRITICAL
        object_validator = "object name"
        validation_check = "check name"
        error_message = "There was an error"
        self.assertFalse(
            models.ModelValidationLog.objects.filter(
                validation_check=validation_check
            ).exists()
        )
        mock_validation_check = Mock(
            validation_runner=Mock(app_name=app, model_name=model),
            level=error_level,
            object_validator=Mock(),
            name=validation_check,
            error_message=error_message,
        )
        mock_validation_check.name = validation_check
        mock_validation_check.object_validator.name = object_validator
        models.ModelValidationLog.log_failed_validation(mock_validation_check)
        self.assertTrue(
            models.ModelValidationLog.objects.filter(
                validation_check=validation_check
            ).exists()
        )
        log = models.ModelValidationLog.objects.get(validation_check=validation_check)
        self.assertEqual(app, log.app)
        self.assertEqual(model, log.model)
        self.assertEqual(error_level.level, log.error_level)
        self.assertEqual(object_validator, log.object_validator)
        self.assertEqual(validation_check, log.validation_check)
        self.assertEqual(error_message, log.error_message)
        self.assertEqual(mock_now(), log.last_seen)
