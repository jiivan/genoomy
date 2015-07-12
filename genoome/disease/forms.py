#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms

class UploadGenomeForm(forms.Form):
    file = forms.FileField()

