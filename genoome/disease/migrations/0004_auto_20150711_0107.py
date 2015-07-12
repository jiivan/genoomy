# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0003_auto_20150711_0058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snpmarker',
            name='rsid',
            field=models.BigIntegerField(),
        ),
    ]
