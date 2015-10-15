# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers
import colorful.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('disease', '0018_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomizedTag',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name', unique=True)),
                ('slug', models.SlugField(max_length=100, verbose_name='Slug', unique=True)),
                ('color_off', colorful.fields.RGBColorField()),
                ('color_on', colorful.fields.RGBColorField()),
                ('show_on_data', models.BooleanField(default=True)),
                ('show_on_landing', models.BooleanField(default=True)),
                ('image', models.ImageField(upload_to='tags/')),
            ],
            options={
                'verbose_name_plural': 'Tags',
                'verbose_name': 'Tag',
            },
        ),
        migrations.CreateModel(
            name='TaggedWhatever',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('object_id', models.IntegerField(db_index=True, verbose_name='Object id')),
                ('content_type', models.ForeignKey(verbose_name='Content type', to='contenttypes.ContentType', related_name='disease_taggedwhatever_tagged_items')),
                ('tag', models.ForeignKey(to='disease.CustomizedTag', related_name='disease_taggedwhatever_items')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='allelecolor',
            options={'verbose_name': 'Variant'},
        ),
        migrations.AlterModelOptions(
            name='snpmarker',
            options={'verbose_name': 'Trai'},
        ),
        migrations.AddField(
            model_name='allelecolor',
            name='tags',
            field=taggit.managers.TaggableManager(through='disease.TaggedWhatever', verbose_name='Tags', to='disease.CustomizedTag', help_text='A comma-separated list of tags.'),
        ),
    ]
