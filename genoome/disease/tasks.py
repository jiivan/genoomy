#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from io import BytesIO
import pickle
import os
import zipfile

from celery import shared_task
from django.core.files.storage import FileSystemStorage

from disease.files_utils import get_genome_filepath, process_filename, \
    parse_raw_genome_file, process_genoome_data, handle_zipped_genome_file

log = logging.getLogger(__name__)

storage = FileSystemStorage()

@shared_task
def recompute_genome_file(genome_filepath):
    with storage.open(genome_filepath, 'rb') as raw_file:
        if zipfile.is_zipfile(raw_file):
            parsed_data = handle_zipped_genome_file(raw_file)
        else:
            parsed_data = parse_raw_genome_file(raw_file)

    data = process_genoome_data(parsed_data)
    buffer = BytesIO()
    pickle.dump(data, buffer)
    dirpath, filename = os.path.split(genome_filepath)
    filename = process_filename(filename, filename_suffix='_processed')
    filepath = os.path.join(dirpath, filename)
    log.debug('Processed filepath: %s', filepath)
    storage.delete(filepath)
    storage.save(filepath, buffer)