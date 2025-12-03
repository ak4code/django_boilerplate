from django.db import models

from commons.mixins.models import AutoTimestampMixin


class ExampleSmall(AutoTimestampMixin, models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name