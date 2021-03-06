"""Update Cloud Commerce User usernames."""

import logging

from ccapi import CCAPI
from django.core.management.base import BaseCommand

from home.models import CloudCommerceUser

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update print audit."""

    help = "Update Cloud Commerce User usernames."

    def handle(self, *args, **options):
        """Update Cloud Commerce User usernames."""
        try:
            cc_users = CCAPI.get_users()
            for user in CloudCommerceUser.unhidden.all():
                try:
                    cc_user = cc_users[user.user_id]
                except KeyError:
                    pass
                else:
                    if cc_user.first_name and cc_user.second_name:
                        user.second_name = cc_user.second_name
                        user.first_name = cc_user.first_name
                        user.save()
        except Exception as e:
            logger.exception("Error updating Cloud Commerce Usernames.")
            raise e
