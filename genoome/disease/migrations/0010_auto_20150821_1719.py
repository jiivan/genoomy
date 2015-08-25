# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0009_auto_20150821_1638'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analyzedataorder',
            name='status',
        ),
        migrations.AddField(
            model_name='analyzedataorder',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='analyzedataorder',
            name='paid',
            field=models.DateTimeField(null=True),
        ),
    ]
