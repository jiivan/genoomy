# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0014_allelecolor_color_alias'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allelecolor',
            name='color_alias',
            field=models.ForeignKey(default=1, to='color_aliases.ColorAlias'),
        ),
    ]
