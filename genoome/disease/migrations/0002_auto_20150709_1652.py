# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snpmarker',
            name='rsid',
            field=models.BigIntegerField(db_index=True, unique=True),
        ),
    ]
