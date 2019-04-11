"""Base Cloud Commerce Updater."""


class BaseCloudCommerceUpdater:
    """Update inventory items in the database and Cloud Commerce."""

    def __init__(self, db_object):
        """Add the db_object to the instance."""
        self.db_object = db_object
