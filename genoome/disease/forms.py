#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from django import forms
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import get_user_model

storage = FileSystemStorage()

class UploadGenomeForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if not self.user.is_authenticated():
            self.fields['email'] = forms.EmailField()

    def clean_file(self):
        if self.user.is_authenticated() and not self.user.can_upload_files:
            raise forms.ValidationError('You already have uploaded genome file.', 'invalid')
        return self.cleaned_data['file']

    def clean_email(self):
        if self.fields.get('email', None) is None:  # Happens when user is not logged in
            return None
        email = self.cleaned_data.get('email', None)
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=email)
            can_upload = user.can_upload_files
        except user_model.DoesNotExist:
            can_upload = True  # Assume that new user can upload files
        if not can_upload:
            raise forms.ValidationError('You can not upload more files', 'invalid')
        return email