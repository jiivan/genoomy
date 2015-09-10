#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from django.core.files.uploadhandler import FileUploadHandler
from django.core.cache import cache

log = logging.getLogger(__name__)

class UploadProgressCachedHandler(FileUploadHandler):
    """
    Tracks progress for file uploads.
    The http post request must contain a header or query parameter, 'X-Progress-ID'
    which should contain a unique string to identify the upload to be tracked.
    """

    def __init__(self, request=None):
        super(UploadProgressCachedHandler, self).__init__(request)
        self.progress_id = None
        self.cache_key = None

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.content_length = content_length
        if 'X-Progress-ID' in self.request.GET:
            self.progress_id = self.request.GET['X-Progress-ID']
        elif 'X-Progress-ID' in self.request.META:
            self.progress_id = self.request.META['X-Progress-ID']
        if self.progress_id:
            self.cache_key = "%s_%s" % (self.request.META['REMOTE_ADDR'], self.progress_id )
            cache.set(self.cache_key, {
                'length': self.content_length,
                'uploaded': 0
            })
            log.debug('PID: %s, Handler cache key: %s', os.getpid(), self.cache_key)
            log.debug('PID: %s, Handle cache: %s', os.getpid(), cache.get(self.cache_key))

    def new_file(self, field_name, file_name, content_type, content_length, charset=None, content_type_extra=None):
        pass

    def receive_data_chunk(self, raw_data, start):
        if self.cache_key:
            data = cache.get(self.cache_key)
            data['uploaded'] += self.chunk_size
            cache.set(self.cache_key, data)
            log.debug('PID: %s, Cache Chunk %s', os.getpid(), data)
        return raw_data

    def file_complete(self, file_size):
        pass

    def upload_complete(self):
        if self.cache_key:
            log.debug('PID: %s, Upload_complete', os.getpid())
            cache.delete(self.cache_key)