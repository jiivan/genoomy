# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0023_auto_20151124_0844'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CeleryTask23',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('chosen_profile', models.TextField()),
                ('fetch_task_id', models.TextField()),
                ('process_task_id', models.TextField(null=True)),
                ('status', models.TextField(choices=[('new', 'new'), ('fetching', 'fetching genome'), ('parsing', 'parsing genome'), ('error', 'error')], default='new')),
                ('analyze_order', models.ForeignKey(to='disease.AnalyzeDataOrder', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Token23',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('access_token', models.TextField()),
                ('refresh_token', models.TextField()),
                ('scope', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
        ),
    ]
