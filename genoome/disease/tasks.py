#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from io import BytesIO
import pickle
import os
import zipfile

from celery import shared_task
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from disease.files_utils import get_genome_dirpath, get_genome_filepath, process_filename, parse_raw_genome_file, process_genoome_data

log = logging.getLogger(__name__)

storage = FileSystemStorage()

@shared_task
def recompute_genome_files(user_pk, user_email):
    task_user = type('TaskUser', (object, ), dict(pk=user_pk, email=user_email))
    genome_dirpath = get_genome_dirpath(task_user)

    if os.path.exists(os.path.join(settings.MEDIA_ROOT, genome_dirpath)):
        _, files = storage.listdir(genome_dirpath)
        for file in files:
            log.debug('Processing file: %s', file)
            filename, ext = file.rsplit('.', 1)
            if filename.endswith('_processed'):
                continue
            with storage.open(get_genome_filepath(task_user, file), 'rb') as raw_file:
                if zipfile.is_zipfile(raw_file):
                    log.debug('Zip file detected')
                    with zipfile.ZipFile(raw_file) as zipped_file,\
                            zipped_file.open('{}.txt'.format(filename)) as unzipped_file:
                        data = process_genoome_data(parse_raw_genome_file(unzipped_file))
                else:
                    data = process_genoome_data(parse_raw_genome_file(raw_file))

                buffer = BytesIO()
                pickle.dump(data, buffer)
                filename = process_filename(file, filename_suffix='_processed')
                filepath = get_genome_filepath(task_user, filename)
                log.debug('Processed filepath: %s', filepath)
                storage.delete(filepath)
                storage.save(filepath, buffer)