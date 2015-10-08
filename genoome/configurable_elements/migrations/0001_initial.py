# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('color_aliases', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegendRow',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('content', models.CharField(max_length=256)),
                ('color', models.ForeignKey(to='color_aliases.ColorAlias')),
            ],
        ),
    ]
