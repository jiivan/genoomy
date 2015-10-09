# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0016_auto_20151007_0824'),
    ]

    operations = [
        migrations.AddField(
            model_name='snpmarkerarticle',
            name='gene_area',
            field=models.CharField(null=True, max_length=256, blank=True),
        ),
    ]
