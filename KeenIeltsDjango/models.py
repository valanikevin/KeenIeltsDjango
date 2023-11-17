from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from randomslugfield import RandomSlugField


class TimestampedBaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        if self.created_at is None:
            self.created_at = timezone.now()

        super(TimestampedBaseModel, self).save(*args, **kwargs)


class SlugifiedBaseModal(models.Model):
    slug = RandomSlugField(length=20, exclude_digits=False)

    class Meta:
        abstract = True


class WeightedBaseModel(models.Model):
    """
    An abstract base model which adds a weight field for ordering objects.
    """
    weight = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        abstract = True
