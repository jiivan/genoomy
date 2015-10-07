# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import colorful.fields

def create_default_color_alias(apps, schema_editor):
    ColorAlias = apps.get_model("color_aliases", "ColorAlias")
    default_color_alias = ColorAlias(color='#7b7979', alias='genoomy_default')
    default_color_alias.save()

def delete_default_color_alias(apps, schema_editor):
    ColorAlias = apps.get_model("color_aliases", "ColorAlias")
    default_color_alias = ColorAlias.objects.get(color='#7b7979', alias='genoomy_default')
    default_color_alias.delete()


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ColorAlias',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('color', colorful.fields.RGBColorField()),
                ('alias', models.CharField(max_length=256)),
            ],
        ),
        migrations.RunPython(create_default_color_alias, delete_default_color_alias)
    ]
