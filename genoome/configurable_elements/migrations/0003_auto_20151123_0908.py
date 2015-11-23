# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('configurable_elements', '0002_auto_20151008_0522'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='legendrow',
            options={'ordering': ['-priority']},
        ),
        migrations.AddField(
            model_name='legendrow',
            name='priority',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
