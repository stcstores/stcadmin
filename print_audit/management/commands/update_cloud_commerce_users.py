"""Management commands for the Print Audit app."""

import logging

from ccapi import CCAPI
from django.core.management.base import BaseCommand

from print_audit.models import CloudCommerceUser

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update print audit."""

    help = "Updates Print Audit"

    def handle(self, *args, **options):
        """Update print audit."""
        try:
            cc_users = CCAPI.get_users()
            for user in CloudCommerceUser.objects.all():
                try:
                    cc_user = cc_users[user.user_id]
                    user.first_name = cc_user.first_name
                    user.second_name = cc_user.second_name
                except IndexError:
                    user.first_name = ""
                    user.second_name = ""
                user.save()
        except Exception as e:
            logger.exception("Error updating Cloud Commerce Usernames.")
            raise e
