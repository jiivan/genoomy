from django.db import models

from color_aliases.models import ColorAlias


class LegendRow(models.Model):
    content = models.CharField(max_length=256)
    color = models.ForeignKey(ColorAlias)
    priority = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-priority']

    def __str__(self):
        return self.content


def get_legend_rows():
    return LegendRow.objects.all()