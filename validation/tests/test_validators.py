from unittest.mock import Mock, patch

from stcadmin.tests.stcadmin_test import STCAdminTest
from validation import models
from validation.base_validation_checks import BaseValidationCheck
from validation.base_validation_runners import ModelValidationRunner, ValidationRunner
from validation.levels import Levels
from validation.object_vaidators import BaseObjectValidator
from validation.run_validation import RunModelValidation


class ValidationCheck(BaseValidationCheck):
    mock_subclass = Mock(level=Levels.FORMATTING)

    def is_valid(*args, **kwargs):
        return True


class InvalidValidationCheck(BaseValidationCheck):
    level = Levels.WARNING

    def is_valid(*args, **kwargs):
        return False

    def format_error_message(self, **test_data):
        return "formatted error message"


class ValidationCheckNoOverrides(BaseValidationCheck):
    pass


class ObjectValidator(BaseObjectValidator):
    name = "Test Object Validator"
    validation_check_class = ValidationCheck


class TmpModelValidationRunner(ModelValidationRunner):
    model = models.ModelValidationLog

    def load_cloud_commerce_data(self):
        pass


class TmpModelValidationRunnerChild(TmpModelValidationRunner):
    pass


class ModelValidationRunnerNoOverride(ModelValidationRunner):
    model = models.ModelValidationLog


class TestLevels(STCAdminTest):
    def test_critical(self):
        self.assertTrue(hasattr(Levels, "CRITICAL"))
        self.assertEqual("Critical", Levels.CRITICAL.name)
        self.assertEqual(10, Levels.CRITICAL.level)

    def test_error(self):
        self.assertTrue(hasattr(Levels, "ERROR"))
        self.assertEqual("Error", Levels.ERROR.name)
        self.assertEqual(7, Levels.ERROR.level)

    def test_warning(self):
        self.assertTrue(hasattr(Levels, "WARNING"))
        self.assertEqual("Warning", Levels.WARNING.name)
        self.assertEqual(4, Levels.WARNING.level)

    def test_formatting(self):
        self.assertTrue(hasattr(Levels, "FORMATTING"))
        self.assertEqual("Formatting", Levels.FORMATTING.name)
        self.assertEqual(2, Levels.FORMATTING.level)

    def test_levels_attrubute(self):
        self.assertTrue(hasattr(Levels, "levels"))
        self.assertEqual(
            [Levels.CRITICAL, Levels.ERROR, Levels.WARNING, Levels.FORMATTING],
            Levels.levels,
        )

    def test_names_attribute(self):
        self.assertTrue(hasattr(Levels, "names"))
        self.assertDictEqual(
            {
                "critical": Levels.CRITICAL,
                "error": Levels.ERROR,
                "warning": Levels.WARNING,
                "formatting": Levels.FORMATTING,
            },
            Levels.names,
        )

    def test_numeric_attribute(self):
        self.assertTrue(hasattr(Levels, "numeric"))
        self.assertDictEqual(
            {
                Levels.CRITICAL.level: Levels.CRITICAL,
                Levels.ERROR.level: Levels.ERROR,
                Levels.WARNING.level: Levels.WARNING,
                Levels.FORMATTING.level: Levels.FORMATTING,
            },
            Levels.numeric,
        )

    def test_level_ordering(self):
        self.assertGreater(Levels.CRITICAL, Levels.FORMATTING)
        self.assertLess(Levels.FORMATTING, Levels.CRITICAL)
        self.assertNotEqual(Levels.FORMATTING, Levels.CRITICAL)

    def test_level_as_int(self):
        self.assertEqual(Levels.CRITICAL.level, int(Levels.CRITICAL))

    def test_level_repr(self):
        self.assertEqual(Levels.CRITICAL.name, repr(Levels.CRITICAL))

    def test_level_html_class(self):
        self.assertEqual(Levels.CRITICAL.name.lower(), Levels.CRITICAL.html_class)

    def test_all_method(self):
        self.assertEqual(
            [Levels.FORMATTING, Levels.WARNING, Levels.ERROR, Levels.CRITICAL],
            Levels.all(),
        )
        self.assertEqual(Levels.all(), sorted(Levels.all()))

    def test_filter(self):
        objects = [Mock(level=i) for i in range(12)]
        returned_objects = Levels.filter(objects=objects, level=Levels.WARNING)
        for obj in returned_objects:
            self.assertGreaterEqual(obj.level, Levels.WARNING.level)

    def test_filter_no_level(self):
        objects = [Mock(level=i) for i in range(12)]
        returned_objects = Levels.filter(objects=objects, level=None)
        self.assertEqual(objects, returned_objects)

    def test_get_with_object(self):
        self.assertEqual(Levels.WARNING, Levels.get(Levels.WARNING))

    def test_get_with_name(self):
        self.assertEqual(Levels.WARNING, Levels.get(Levels.WARNING.name))

    def test_get_with_level(self):
        self.assertEqual(Levels.WARNING, Levels.get(Levels.WARNING.level))

    def test_get_with_invalid_identifier(self):
        with self.assertRaises(ValueError):
            Levels.get("invalid")


class TestObjectValidator(STCAdminTest):
    @patch("validation.object_vaidators.all_subclasses")
    def test_init(self, mock_all_subclasses):
        mock_subclass = Mock()
        mock_all_subclasses.return_value = {mock_subclass}
        runner = ValidationRunner()
        validator = ObjectValidator(runner)
        self.assertEqual([], validator.error_messages)
        self.assertEqual([], validator.invalid_objects)
        self.assertEqual(runner, validator.validation_runner)
        self.assertEqual({mock_subclass}, validator.validation_checks)

    def test_get_test_objects(self):
        runner = ValidationRunner()
        validator = ObjectValidator(runner)
        with self.assertRaises(NotImplementedError):
            validator.get_test_objects(runner)

    @patch("validation.object_vaidators.all_subclasses")
    def test_validate_all_method(self, mock_all_subclasses):
        mock_subclass = Mock()
        mock_all_subclasses.return_value = {mock_subclass}
        mock_object = Mock()
        runner = ValidationRunner()
        validator = ObjectValidator(runner)
        validator.get_test_objects = lambda x: [mock_object]
        validator.validate_all()
        mock_subclass.assert_called_once_with(validator, runner, mock_object)


class TestValidationRunner(STCAdminTest):
    def test_init(self):
        runner = ValidationRunner()
        self.assertEqual([], runner.failed_validations)
        self.assertIsNone(runner.level)
        self.assertEqual({level: [] for level in Levels.levels}, runner.levels)
        self.assertEqual(runner.validators, {})

    def test_load_validators(self):
        runner = ValidationRunner()
        runner.validator_classes = [ObjectValidator]
        validators = runner.load_validators()
        self.assertEqual(1, len(validators))
        self.assertIn(ObjectValidator.name, validators)
        self.assertIsInstance(validators[ObjectValidator.name], ObjectValidator)

    @patch("validation.object_vaidators.all_subclasses")
    def test_validate(self, mock_all_subclasses):
        mock_subclass = Mock()
        mock_all_subclasses.return_value = {mock_subclass}
        mock_object = Mock()
        runner = ValidationRunner()
        runner.validator_classes = [ObjectValidator]
        runner.validators = runner.load_validators()
        validator = runner.validators[ObjectValidator.name]
        validator.get_test_objects = lambda x: [mock_object]
        runner.validate()
        mock_subclass.assert_called_with(validator, runner, mock_object)

    def test_error_messages(self):
        runner = ValidationRunner()
        failed_validation = Mock()
        runner.failed_validations = [failed_validation]
        self.assertEqual([str(failed_validation)], runner.error_messages())

    def test_format_error_messages(self):
        runner = ValidationRunner()
        failed_validations = [Mock(), Mock()]
        runner.failed_validations = failed_validations
        self.assertEqual(
            "{}\n{}".format(*failed_validations), runner.format_error_messages()
        )

    def test_add_failed_validation(self):
        runner = ValidationRunner()
        mock_validation = Mock(level=Levels.CRITICAL)
        runner.add_failed_validation(mock_validation)
        self.assertEqual(runner.levels[Levels.CRITICAL], [mock_validation])

    def test_add_failed_validation_with_invalid_level(self):
        runner = ValidationRunner()
        mock_validation = Mock(level=None)
        with self.assertRaises(ValueError):
            runner.add_failed_validation(mock_validation)
        self.assertEqual(runner.levels[Levels.CRITICAL], [])


class TestModelValidationRunner(STCAdminTest):
    fixtures = ("validation/model_validation_log",)

    def test_init(self):
        runner = TmpModelValidationRunner()
        self.assertEqual([], runner.failed_validations)
        self.assertIsNone(runner.level)
        self.assertEqual({level: [] for level in Levels.levels}, runner.levels)
        self.assertEqual(runner.validators, {})
        self.assertEqual(
            set(models.ModelValidationLog.objects.all()), set(runner.model_objects)
        )

    def test_app_name(self):
        runner = TmpModelValidationRunner()
        self.assertEqual("validation", runner.app_name)

    def test_model_name(self):
        runner = TmpModelValidationRunner()
        self.assertEqual("ModelValidationLog", runner.model_name)

    def test_get_instances(self):
        instances = TmpModelValidationRunner.get_instances()
        self.assertIsInstance(instances, list)
        self.assertEqual(1, len(instances))
        self.assertIsInstance(instances[0], TmpModelValidationRunnerChild)

    def test_exception_raised_when_load_cloud_commerce_date_is_not_overriden(self):
        with self.assertRaises(NotImplementedError):
            ModelValidationRunnerNoOverride()


class TestValidationCheck(STCAdminTest):
    def setUp(self):
        super().setUp()
        self.validation_runner = ValidationRunner()
        self.object_validator = ObjectValidator(self.validation_runner)
        self.validation_object = Mock()

    def get_validation_check(self, validation_check_class=ValidationCheck):
        validation_check = validation_check_class(
            self.object_validator, self.validation_runner, self.validation_object
        )
        return validation_check

    def test_init(self):
        validation_check = self.get_validation_check()
        self.assertEqual(self.validation_runner, validation_check.validation_runner)
        self.assertEqual(self.object_validator, validation_check.object_validator)
        self.assertEqual(self.validation_object, validation_check.validation_object)
        self.assertEqual("", validation_check.error_message)
        self.assertEqual(self.validation_runner, validation_check.validation_runner)

    def test_repr(self):
        validation_check = self.get_validation_check()
        validation_check.name = "check_name"
        self.assertEqual("Validation Check: check_name", repr(validation_check))

    def test_str(self):
        validation_check = self.get_validation_check()
        validation_check.level = Levels.WARNING
        validation_check.error_message = "error message"
        self.assertEqual("Warning: error message", str(validation_check))

    def test_is_valid(self):
        with self.assertRaises(NotImplementedError):
            self.get_validation_check(validation_check_class=ValidationCheckNoOverrides)

    def test_format_error_message(self):
        validation_check = self.get_validation_check()
        with self.assertRaises(NotImplementedError):
            validation_check.format_error_message({})

    def test_contains_whitespace(self):
        validation_check = self.get_validation_check()
        self.assertFalse(validation_check.contains_whitespace("hello"))
        self.assertFalse(validation_check.contains_whitespace("hello world"))
        self.assertTrue(validation_check.contains_whitespace("hello world "))
        self.assertTrue(validation_check.contains_whitespace(" hello world"))
        self.assertTrue(validation_check.contains_whitespace("hello world\n"))

    def test_validate_valid(self):
        validation_check = self.get_validation_check()
        mock_object = Mock()
        validation_check.validate(mock_object)
        self.assertEqual("", validation_check.error_message)
        self.assertEqual(0, len(self.validation_runner.failed_validations))

    def test_validate_invalid(self):
        validation_check = self.get_validation_check(
            validation_check_class=InvalidValidationCheck
        )
        mock_object = Mock()
        validation_check.validate(mock_object)
        self.assertEqual("formatted error message", validation_check.error_message)
        self.assertIn(validation_check, self.validation_runner.failed_validations)

    def test_ordering(self):
        critical_validation_check = self.get_validation_check()
        critical_validation_check.level = Levels.CRITICAL
        error_validation_check = self.get_validation_check()
        error_validation_check.level = Levels.ERROR
        self.assertGreater(error_validation_check, critical_validation_check)


class TestRunModelValidation(STCAdminTest):
    @patch("validation.run_validation.models.ModelValidationLog")
    @patch("validation.run_validation.ModelValidationRunner")
    def test_run(self, mock_ModelValidationRunner, mock_ModelValiationLog):
        runner = Mock(failed_validations=[])
        mock_ModelValidationRunner.get_instances.return_value = [runner]
        RunModelValidation.run()
        mock_ModelValidationRunner.get_instances.assert_called_once()
        runner.validate.assert_called_once()

    @patch("validation.run_validation.models.ModelValidationLog")
    def test_log_runner(self, mock_ModelValiationLog):
        failed_validation = Mock()
        runner = Mock(failed_validations=[failed_validation])
        RunModelValidation.log_runner(runner)
        mock_ModelValiationLog.clear_validation_runner.assert_called_once_with(runner)
        mock_ModelValiationLog.log_failed_validation.assert_called_once_with(
            failed_validation
        )
