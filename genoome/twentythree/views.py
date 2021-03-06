from celery.result import AsyncResult
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import FormView
import logging
import urllib.parse

from twentythree.forms import ChooseProfileForm
from twentythree.models import CeleryTask23
from twentythree.models import Token23

log = logging.getLogger('genoome.twentythree.views')

def token_required(f):
    def inner(request, *args, **kwargs):
        has_token = request.user.token23_set.exists()
        if not has_token:
            return HttpResponseRedirect(reverse_lazy('23andme:login'))
        return f(request, *args, **kwargs)
    return inner

class TokenMixin(object):
    def get_token(self):
        token = Token23.objects.get(user=self.request.user)
        return token

@login_required(login_url=reverse_lazy('accounts:signin'))
def login23(request):
    try:
        token = Token23.objects.get(user=request.user)
    except Token23.DoesNotExist:
        pass
    else:
        log.info('Trying to refresh old token...')
        try:
            token.refresh()
            return HttpResponseRedirect(reverse_lazy('23andme:profiles'))
        except Token23.ClientError:
            log.info('Refreshing token failed. Asking for a new one...')
    # https://api.23andme.com/docs/authentication/ 
    url = 'https://api.23andme.com/authorize/?redirect_uri=%s&response_type=code&client_id=%s&scope=basic%%20genomes'
    url %= (
        urllib.parse.quote(settings.COMEBACK_URL23),
        settings.CLIENT_ID23,
    )
    return HttpResponseRedirect(url)

def comeback(request):
    try:
        code = request.GET['code']
    except KeyError:
        log.info('No code. Redirecting to 23andme_login(%s)', request.user)
        return HttpResponseRedirect(reverse_lazy('23andme:login'))
    try:
        token = Token23.get_by_code(request.user, code)
    except Token23.ClientError:
        log.error('Failed token(%r). Redirecting to 23andme_login(%s)', code, request.user)
        return HttpResponseRedirect(reverse_lazy('23andme:login'))
    return HttpResponseRedirect(reverse_lazy('23andme:profiles'))

class ChooseProfileView(FormView, TokenMixin):
    form_class = ChooseProfileForm
    success_url = reverse_lazy('23andme:status')
    template_name = 'twentythree/choose_profile.html'

    def get(self, request, *args, **kwargs):
        profiles = self.get_token().get_profiles()
        genotyped_profiles = [p for p in profiles if p['genotyped']]
        if len(genotyped_profiles) == 1:
            # use this profile
            form = self.get_form()
            return self.form_valid(form)
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['profiles'] = self.get_token().get_profiles()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

profiles = login_required(token_required(ChooseProfileView.as_view()), login_url=reverse_lazy('accounts:signin'))

@login_required(login_url=reverse_lazy('accounts:signin'))
@token_required
def status(request):
    try:
        ctask = CeleryTask23.objects.filter(user=request.user).order_by('-pk')[0]
    except CeleryTask23.DoesNotExist:
        return HttpResponseRedirect(raverse_lazy('23andme:profiles'))
    context = {}
    context['ctask'] = ctask
    context['job'] = job = AsyncResult(ctask.fetch_task_id)
    if ctask.analyze_order:
        analyze_job = AsyncResult(ctask.analyze_order.task_uuid)
    else:
        analyze_job = None
    context['analyze_job'] = analyze_job
    if not job.ready():
        messages.add_message(request, messages.INFO,
                             'Your genome data is being fetched. Please wait a few seconds...')
    elif job.failed():
        messages.add_message(request, settings.DANGER,
                             "An error occured while processing your genome data. Let us check what is going on. And we will contact you soon.")
    else:
        if (analyze_job is None) or (not analyze_job.ready()):
            messages.add_message(request, messages.INFO,
                                 'Your genome data is being analyzed. Please wait a few seconds...')
        elif analyze_job.failed():
            messages.add_message(self.request, settings.DANGER,
                                 "An error occured while processing your genome data. Let us check what is going on. And we will contact you soon.")
        else:
            # redirect
            file = ctask.analyze_order.uploaded_filename
            return HttpResponseRedirect("%s?file=%s" % (reverse_lazy('disease:browse_genome'), urllib.parse.quote(file)))
    return render(request, 'twentythree/status.html', context)
