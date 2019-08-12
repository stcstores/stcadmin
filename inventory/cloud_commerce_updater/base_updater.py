"""Base Cloud Commerce Updater."""
import logging

logger = logging.getLogger("product_editor")


class BaseCloudCommerceUpdater:
    """Update inventory items in the database and Cloud Commerce."""

    LOGGING_LEVEL = logging.INFO
    LOG_MESSAGE = None
    update_DB = False
    update_CC = False

    def __init__(self, db_object, user):
        """Add the db_object to the instance."""
        self.db_object = db_object
        self.user = user

    def log(self, message, level=None):
        """Add a logging message."""
        logger.log(
            level or self.LOGGING_LEVEL,
            self.LOG_MESSAGE.format(self.user, self.db_object.SKU, message),
        )
