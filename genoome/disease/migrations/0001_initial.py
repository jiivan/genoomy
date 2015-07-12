# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SNPMarker',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('rsid', models.BigIntegerField(db_index=True)),
                ('link', models.TextField()),
                ('risk_allele', models.CharField(max_length=128)),
                ('disease_trait', models.TextField()),
                ('p_value', models.FloatField()),
                ('or_or_beta', models.FloatField()),
            ],
        ),
    ]
