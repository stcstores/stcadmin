"""The CloudCommerceShippingRule model class."""

from django.db import models


class CloudCommerceShippingRule(models.Model):
    """Model for Cloud Commerce Shipping Rules."""

    class Meta:
        """Meta class for the CloudCommerceShippingRule model."""

        verbose_name = 'Cloud Commerce Shipping Rule'
        verbose_name_plural = 'Cloud Commerce Shipping Rules'

    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    rule_id = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.rule_id} - {self.name}'
