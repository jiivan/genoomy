# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0002_auto_20150709_1652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snpmarker',
            name='or_or_beta',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='snpmarker',
            name='p_value',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
