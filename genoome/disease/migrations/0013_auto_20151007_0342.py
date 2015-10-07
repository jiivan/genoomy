# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_markdown.models


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0012_snpmarkerarticle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allelecolor',
            name='description',
            field=django_markdown.models.MarkdownField(),
        ),
    ]
