from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
import logging
import urllib.parse

from twentythree.forms import ChooseProfileForm

log = logging.getLogger('genoome.twentythree.views')

def token_required(f):
    def inner(request, *args, **kwargs):
        has_token = request.user.token23_set.exists()
        if not has_token:
            return HttpResponseRedirect(reverse_lazy('23andme:login'))
        return f(request, *args, **kwargs)
    return inner

@login_required(login_url=reverse_lazy('accounts:signin'))
def login23(request):
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
        token = Token.get_by_code(request.user, code)
    except Token.ClientError:
        log.error('Failed token(%r). Redirecting to 23andme_login(%s)', code, request.user)
    return HttpResponseRedirect(reverse_lazy('23andme:profiles'))

class ChooseProfileView(FormView):
    form_class = ChooseProfileForm
    success_url = reverse_lazy('23andme:status')
    template_name = 'twentythree/choose_profile.html'

    def get(self, request, *args, **kwargs):
        self.get_token().get_profiles()
        genotyped_profiles = [p for p in profiles if p['genotyped']]
        if len(genotyped_profiles) == 1:
            # use this profile
            form = self.get_form()(self.get_form_kwargs())
            return self.form_valid(form)
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = self.get_form_kwargs()
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
    if ctask.status == 'parsing':
        return HttpResponseRedirect(genomeurl)
    return render_to_response('twentythree/status.html', {'ctask': ctask})
