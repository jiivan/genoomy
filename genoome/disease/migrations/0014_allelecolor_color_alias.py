# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('color_aliases', '0001_initial'),
        ('disease', '0013_auto_20151007_0342'),
    ]

    operations = [
        migrations.AddField(
            model_name='allelecolor',
            name='color_alias',
            field=models.ForeignKey(blank=True, null=True, to='color_aliases.ColorAlias'),
        ),
    ]
