#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from django import forms
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .files_utils import get_genome_dirpath

storage = FileSystemStorage()

class UploadGenomeForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_file(self):
        dirpath = get_genome_dirpath(self.user)
        _, files = storage.listdir(os.path.join(settings.MEDIA_ROOT, dirpath))
        if len(files) > 0:
            raise forms.ValidationError('You already have uploaded genome file.', 'invalid')
        return self.cleaned_data['file']


