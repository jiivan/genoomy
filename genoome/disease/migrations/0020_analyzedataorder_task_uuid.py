# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0019_auto_20151014_2359'),
    ]

    operations = [
        migrations.AddField(
            model_name='analyzedataorder',
            name='task_uuid',
            field=models.CharField(default=datetime.datetime(2015, 10, 22, 16, 24, 27, 545622, tzinfo=utc), max_length=256),
            preserve_default=False,
        ),
    ]
