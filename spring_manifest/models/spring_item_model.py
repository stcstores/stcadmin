from ccapi import CCAPI
from django.db import models

from .spring_package_model import SpringPackage


class SpringItem(models.Model):

    class Meta:
        ordering = ('item_id', )

    package = models.ForeignKey(SpringPackage, on_delete=models.CASCADE)
    item_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return '{}_{}'.format(str(self.package), self.item_id)

    def get_item(self):
        return CCAPI.get_product(self.item_id)
