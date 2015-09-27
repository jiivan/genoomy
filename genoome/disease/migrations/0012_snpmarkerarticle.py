# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_markdown.models


class Migration(migrations.Migration):

    dependencies = [
        ('disease', '0011_allelecolor_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='SNPMarkerArticle',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(help_text='Title for SNM description page', max_length=128)),
                ('header', django_markdown.models.MarkdownField(help_text='Introductory text appearing in header section of SNP description')),
                ('footer', django_markdown.models.MarkdownField(help_text='Place for footer, bibliography etc.')),
                ('snp_marker', models.ForeignKey(to='disease.SNPMarker', related_name='snp_article')),
            ],
        ),
    ]
