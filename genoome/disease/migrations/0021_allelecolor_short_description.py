# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0020_analyzedataorder_task_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='allelecolor',
            name='short_description',
            field=models.CharField(blank=True, null=True, max_length=128),
        ),
    ]
