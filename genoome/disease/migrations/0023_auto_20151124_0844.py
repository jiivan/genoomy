# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0022_auto_20151116_0944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allelecolor',
            name='short_description',
            field=models.CharField(blank=True, null=True, help_text='Variant description', max_length=256),
        ),
    ]
