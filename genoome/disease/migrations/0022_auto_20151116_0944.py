# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0021_allelecolor_short_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allelecolor',
            name='short_description',
            field=models.CharField(null=True, blank=True, max_length=128, help_text='Variant description'),
        ),
        migrations.AlterField(
            model_name='customizedtag',
            name='image',
            field=models.ImageField(null=True, blank=True, upload_to='tags/'),
        ),
    ]
