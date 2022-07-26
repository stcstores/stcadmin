"""Model containing config for managing Shopify."""

from django.db import models
from solo.models import SingletonModel


class ShopifyConfig(SingletonModel):
    """Model for storing config data for managing Shopify."""

    location_id = models.PositiveIntegerField()
