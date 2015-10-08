# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

color_map = [
    ('#0080ff', 'blue'),
    ('#00ff00', 'green'),
    ('#ff8000', 'orange'),
    ('#ffff00', 'yellow'),
    ('#f54949', 'red')
]

def forward_migrate_colors(apps, schema_editor):
    ColorAlias = apps.get_model('color_aliases', 'ColorAlias')
    AlleleColor = apps.get_model('disease', 'AlleleColor')
    for hex_color, color_name in color_map:
        calias = 'genoomy_{}'.format(color_name)
        color_alias, _ = ColorAlias.objects.get_or_create(color=hex_color, alias=calias)
        AlleleColor.objects.filter(color=hex_color).update(color_alias=color_alias)

def backward_migrate_colors(apps, schema_editor):
    ColorAlias = apps.get_model('color_aliases', 'ColorAlias')
    AlleleColor = apps.get_model('disease', 'AlleleColor')
    default_color_alias, _ = ColorAlias.objects.get_or_create(alias='genoomy_default')
    AlleleColor.objects.all().update(color_alias=default_color_alias)


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0015_auto_20151007_0410'),
    ]

    operations = [
        migrations.RunPython(forward_migrate_colors, backward_migrate_colors)
    ]
