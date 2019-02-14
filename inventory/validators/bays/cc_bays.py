"""Validate Cloud Commerce Bays."""

from validation import BaseObjectValidator, BaseValidationCheck, Levels


class CCBayValidationCheck(BaseValidationCheck):
    """Base validation checker for Cloud Commerce Warehouses."""

    def get_matching_model_object(self, object):
        """Return the matching database object for a bay.

        Return None if no database object matches the bay.
        """
        for model_object in self.validation_runner.model_objects:
            if model_object.warehouse_id == object.id:
                return model_object
        return None


class CCBayValidator(BaseObjectValidator):
    """Validate Cloud Commerce Warehouses."""

    name = "Cloud Commerce Bay"
    validation_check_class = CCBayValidationCheck

    def get_test_objects(self, validation_runner):
        """Return a list of objects to validate."""
        return validation_runner.cc_bays


class CCBayInDb(CCBayValidationCheck):
    """Check a Cloud Commerce Bay exists in the Bay database model."""

    name = "Bay misssing from Database"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a Cloud Commerce Bay exists in the Bay database model."""
        model_object_IDs = [o.bay_id for o in kwargs["validation_runner"].model_objects]
        if int(kwargs["test_object"].id) not in model_object_IDs:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f"No Bay exists in the database matching the ID of "
            f'"{kwargs["test_object"].name}" ("{kwargs["test_object"].id}").'
        )
