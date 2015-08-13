# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0006_allelecolor'),
    ]

    operations = [
        migrations.AddField(
            model_name='allelecolor',
            name='snp_marker',
            field=models.ForeignKey(default=-1, to='disease.SNPMarker'),
            preserve_default=False,
        ),
    ]
