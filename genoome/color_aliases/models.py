from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from colorful.fields import RGBColorField


class ColorAlias(models.Model):
    color = RGBColorField()
    alias = models.CharField(max_length=256)

    def __str__(self):
        return self.alias

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from disease.models import SNPMarker
        for marker in SNPMarker.objects.filter(allele_colors__color_alias=self):
            marker.invalidate_colors()
