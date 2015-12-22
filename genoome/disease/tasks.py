#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from io import BytesIO
import os
import zipfile

from django.core.files.storage import FileSystemStorage
import msgpack

from celery import task
from disease.files_utils import get_genome_filepath, process_filename, \
    parse_raw_genome_file, process_genoome_data, handle_zipped_genome_file

log = logging.getLogger(__name__)

storage = FileSystemStorage()

@task
def recompute_genome_file(genome_filepath):
    log.debug('Genome filepath: %s', genome_filepath)
    with storage.open(genome_filepath, 'r') as raw_file:
        if zipfile.is_zipfile(storage.path(genome_filepath)):
            parsed_data = handle_zipped_genome_file(storage.path(genome_filepath))
        else:
            parsed_data = parse_raw_genome_file(raw_file)

    data = process_genoome_data(parsed_data)
    buffer = BytesIO()
    msgpack.pack(data, buffer)
    dirpath, filename = os.path.split(genome_filepath)
    filename = process_filename(filename, filename_suffix='_processed')
    filepath = os.path.join(dirpath, filename)
    log.debug('Processed filepath: %s', filepath)
    storage.delete(filepath)
    storage.save(filepath, buffer)