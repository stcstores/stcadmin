from django.db import models

from .spring_order_model import SpringOrder


class SpringPackage(models.Model):

    class Meta:
        unique_together = ('package_number', 'order', )
        ordering = ('package_number', )

    package_number = models.PositiveIntegerField(default=1)
    order = models.ForeignKey(SpringOrder, on_delete=models.CASCADE)

    def package_id(self):
        return '{}_{}'.format(self.order.order_id, self.package_number)

    def __str__(self):
        return self.package_id()
