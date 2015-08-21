# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('disease', '0008_auto_20150814_0740'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalyzeDataOrder',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('uploaded_filename', models.CharField(max_length=256)),
                ('status', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='analyzedataorder',
            unique_together=set([('user', 'uploaded_filename')]),
        ),
    ]
