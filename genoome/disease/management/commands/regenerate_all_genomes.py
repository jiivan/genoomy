#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from disease.files_utils import get_genome_filepath
from disease.tasks import recompute_genome_file


class Command(BaseCommand):
    def handle(self, **options):
        for user in get_user_model().objects.all().order_by('-pk'):
            for filename in user.uploaded_files:
                filepath = get_genome_filepath(user, filename)
                recompute_genome_file.apply_async(args=(filepath,))
