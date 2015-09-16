# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0010_auto_20150821_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='allelecolor',
            name='description',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
