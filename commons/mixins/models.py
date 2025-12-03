from django.db import models


class AutoTimestampMixin(models.Model):
    """Mixin добавляет автоматические поля created_at и updated_at временных меток в модель."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        abstract = True