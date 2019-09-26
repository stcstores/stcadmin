"""Base test classes."""
from django.test import TestCase, override_settings


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
@override_settings(CC_DOMAIN="nowhere@nowhere.com")
@override_settings(CC_USERNAME="username")
@override_settings(CC_USERNAME="password")
class STCAdminTest(TestCase):
    """Base class for tests."""

    pass
