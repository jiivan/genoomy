# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0004_auto_20150711_0107'),
    ]

    operations = [
        migrations.AddField(
            model_name='snpmarker',
            name='comment',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
