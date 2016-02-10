from celery import uuid as celery_uuid
from django import forms
import itertools
import logging

from disease.files_utils import get_genome_filepath
from twentythree.tasks import fetch_genome_and_push_forward
from twentythree.models import CeleryTask23

log = logging.getLogger('genoome.twentythree.forms')

class ChooseProfileForm(forms.Form):
    profile = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        self.profiles = kwargs.pop('profiles')
        self.genotyped_profiles = [p['id'] for p in self.profiles if p['genotyped']]
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        cnt = itertools.count()
        self.fields['profile'].choices = [ (next(cnt), p_id) for p_id in sorted(self.genotyped_profiles) ]

    def clean_profile(self):
        profile_id = self.genotyped_profiles[int(self.cleaned_data['profile'])]
        return profile_id

    def save(self):
        if len(self.genotyped_profiles) == 1:
            profile_id = self.genotyped_profiles[0]
        else:
            profile_id = self.cleaned_data['profile']
        celery_task_id = celery_uuid()

        ctask = CeleryTask23.objects.create(user=self.user, chosen_profile=profile_id, fetch_task_id=celery_task_id)
        fetch_genome_and_push_forward.apply_async(args=(ctask.pk,), task_id=ctask.fetch_task_id)
        return ctask
