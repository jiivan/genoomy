# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0016_auto_20151007_0824'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='allelecolor',
            name='color',
        ),
    ]
