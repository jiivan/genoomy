# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0007_allelecolor_snp_marker'),
    ]

    operations = [
        migrations.AddField(
            model_name='allelecolor',
            name='priority',
            field=models.PositiveIntegerField(default=100),
        ),
        migrations.AlterField(
            model_name='allelecolor',
            name='snp_marker',
            field=models.ForeignKey(to='disease.SNPMarker', related_name='allele_colors'),
        ),
    ]
