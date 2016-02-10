from celery import uuid as celery_uuid
from django import forms
import itertools
import logging

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

        defaults = {
            'chosen_profile': profile_id,
            'fetch_task_id': celery_task_id,
        }
        ctask, created = CeleryTask23.objects.get_or_create(user=self.user, defaults=defaults)
        if not created:
            log.warning('Updating old task for %s', self.user)
            for key in defaults:
                setattr(ctask, key, defaults[key])
        fetch_genome_and_push_forward.apply_async(args=(ctask.pk,), task_id=ctask.fetch_task_id)
        log.info('Created celery task: %s for %s', ctask.fetch_task_id, self.user)
        return ctask
