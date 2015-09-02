from datetime import datetime
from io import BytesIO
import json
import logging
import uuid
import pickle
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponseServerError
from django.http import HttpResponse
from django.views.generic import FormView
from django.views.generic.edit import ProcessFormView
from django.views.generic import TemplateView
from django.utils import timezone
from django.contrib.auth import login

from paypal.standard.forms import PayPalPaymentsForm

from disease.files_utils import process_filename
from disease.files_utils import get_genome_dirpath
from disease.files_utils import get_genome_filepath
from .forms import UploadGenomeForm
from .models import AnalyzeDataOrder
from .tasks import recompute_genome_files

log = logging.getLogger(__name__)

storage = FileSystemStorage()

def upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    progress_id = ''
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    if progress_id:
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        log.debug('PID: %s, Upload progress cache %s',os.getpid(),  data)
        if data is None:
            data = {'length': 1, 'uploaded': 1}
        return JsonResponse(data)
    else:
        return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')


class GenomeFilePathMixin(object):

    def process_filename(self, filename, filename_suffix=None):
        return process_filename(filename, filename_suffix)

    def get_dirpath(self, user=None):
        if user is None:
            user = self.request.user
        return get_genome_dirpath(user)

    def get_filepath(self, filename, user=None):
        if user is None:
            user = self.request.user
        return get_genome_filepath(user, filename)

class UploadGenome(GenomeFilePathMixin, FormView):
    template_name = 'upload_genome.html'
    form_class = UploadGenomeForm
    success_url = reversed('disease:genome_payment')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        form = self.get_form()
        upload_id = uuid.uuid4()
        return self.render_to_response(self.get_context_data(form=form, upload_id=upload_id))

    def save_processed_data(self, data):
        buffer = BytesIO()
        pickle.dump(data, buffer)
        filename = self.process_filename(self.request.FILES['file'].name, filename_suffix='_processed')
        storage.save(self.get_filepath(filename), buffer)

    def form_valid(self, form):
        # save file
        # create AnalyzeFileOrder
        # raw_filepath = self.get_filepath(raw_filename)
        cd = form.cleaned_data
        email = cd.get('email', None)
        raw_file = cd.get('file', None)
        raw_filename = getattr(raw_file, 'name', None)
        user_model = get_user_model()
        if not self.request.user.is_authenticated():
            try:
                user = user_model.objects.get(email=email)
            except user_model.DoesNotExist:  # user doesn't have an account, create one
                user = user_model(email=email, username=email)
                user.save()

                # Dirty hack to allow user login by model
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(self.request, user)

            # Dirty hack to fix some parts requiring request.user...
            self.request.user = user
        else:
            user = self.request.user

        storage.save(self.get_filepath(raw_filename, user=user), raw_file)
        analyze_order = AnalyzeDataOrder(uploaded_filename=raw_filename, user=user)

        if user.is_staff and user.is_active:
            log.info('User %s skipping payment due to staff membership', user)
            analyze_order.paid = timezone.now()
        analyze_order.save()
        recompute_genome_files.delay(user.pk, user.email)
        # table = process_genoome_data(data)
        # file_exists = os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.get_filepath(self.process_filename(raw_filename, filename_suffix='_processed'))))
        # if self.request.user.is_authenticated() and not file_exists:
        #     self.save_processed_data(table)

        # ctx = self.get_context_data(form=form, table=table, analyzed=True)
        pos_data = analyze_order.posData()
        ctx = self.get_context_data(
            form=form, analyzed=True, pos_data=pos_data, bitpay_checkout_url=settings.BITPAY_API,
            analyze_data_order_pk=analyze_order.pk,
            paypal_form=PayPalPaymentsForm(
                initial=analyze_order.paypal_data(self.request))
            )
        return self.render_to_response(ctx)

class GenomePaymentView(TemplateView):
    template_name = 'upload_success.html'


class DisplayGenomeResult(GenomeFilePathMixin, TemplateView):
    template_name = 'display_genome_result.html'

    def get(self, request, *args, **kwargs):
        self.user = self.request.user
        if self.is_browsing_via_admin:
            self.user = get_user_model().objects.get(pk=int(self.request.GET['pk']))
        return super().get(request, *args, **kwargs)

    def get_genome_data(self):
        filename = self.process_filename(self.request.GET['file'], filename_suffix='_processed')
        filepath = self.get_filepath(filename)
        with storage.open(filepath) as f:
            data = pickle.load(f)
        return data

    @property
    def is_admin(self):  # TODO use permissions?
        return bool(self.request.user.is_staff and self.request.user.is_active)

    @property
    def is_browsing_via_admin(self):
        return bool(('pk' in self.request.GET) and self.is_admin)

    def get_filepath(self, filename):
        if self.is_browsing_via_admin:
            return get_genome_filepath(self.user, filename)
        return super().get_filepath(filename)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_admin'] = is_admin = self.is_admin

        order_kwargs = dict(uploaded_filename=self.request.GET['file'], user=self.user)
        paid = False

        try:
            analyze_data_order = AnalyzeDataOrder.objects.get(**order_kwargs)
            paid = analyze_data_order.is_paid
        except AnalyzeDataOrder.DoesNotExist:
            if not self.is_browsing_via_admin:
                analyze_data_order = AnalyzeDataOrder(**order_kwargs)
                analyze_data_order.save()
                paid = analyze_data_order.is_paid

        ctx['paid'] = paid
        if paid or is_admin:
            ctx['table'] = self.get_genome_data()
        ctx['bitpay_checkout_url'] = settings.BITPAY_API
        ctx['analyze_data_order_pk'] = analyze_data_order.pk
        ctx['pos_data'] = analyze_data_order.posData()
        ctx['paypal_form'] = PayPalPaymentsForm(
            initial=analyze_data_order.paypal_data(self.request))
        return ctx


class PaymentStatusView(ProcessFormView, TemplateView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        post_data = self.request.POST
        print(post_data)
        if post_data['status'] in {'paid', 'complete', 'confirmed'}:
            posData = json.loads(post_data['posData'])
            analyze_order_pk = posData['analyze_order_pk']
            user_pk = posData['user_pk']

            analyze_order = AnalyzeDataOrder.objects.get(pk=analyze_order_pk)
            analyze_order.paid = timezone.now()
            analyze_order.save()
        return HttpResponse('OK')

