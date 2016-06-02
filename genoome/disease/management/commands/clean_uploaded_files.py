#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import FileSystemStorage

from disease.files_utils import get_genome_dirpath, get_genome_filepath


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('username', metavar='username')

    def handle(self, username, **options):
        user = get_user_model().objects.get(username=username)
        user.analyzedataorder_set.all().delete()
        user.couponredeemed_set.all().delete()

        genome_files_dir = get_genome_dirpath(user)
        storage = FileSystemStorage()

        dirs, files = storage.listdir(genome_files_dir)
        for file in files:
            storage.delete(get_genome_filepath(user, file))
