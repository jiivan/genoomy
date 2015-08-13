# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import colorful.fields


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0005_snpmarker_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlleleColor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('color', colorful.fields.RGBColorField()),
                ('allele', models.CharField(max_length=128)),
            ],
        ),
    ]
