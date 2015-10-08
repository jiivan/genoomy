# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


legend_map = [
    ('#0080ff', 'Interesting'),
    ('#00ff00', 'Positive'),
    ('#ff8000', 'Disadvantage'),
    ('#ffff00', 'Neutral'),
    ('#f54949', 'Very negative')
]


def forward_make_legend(apps, schema_editor):
    ColorAlias = apps.get_model('color_aliases', 'ColorAlias')
    LegendRow = apps.get_model('configurable_elements', 'LegendRow')
    for hex_color, content in legend_map:
        color_alias = ColorAlias.objects.get(color=hex_color)
        LegendRow(content=content, color=color_alias).save()

def backward_make_legend(apps, schema_editor):
    LegendRow = apps.get_model('configurable_elements', 'LegendRow')
    LegendRow.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('configurable_elements', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward_make_legend, backward_make_legend)
    ]
