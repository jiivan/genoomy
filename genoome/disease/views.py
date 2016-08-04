from io import BytesIO
import json
import logging
import uuid
import os

from celery import uuid as celery_uuid
from celery.result import AsyncResult
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import reverse_lazy
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponseServerError
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from django.views.generic.edit import ProcessFormView
from django.views.generic import TemplateView
from django.utils import timezone
import msgpack

from paypal.standard.forms import PayPalPaymentsForm

from disease.files_utils import process_filename
from disease.files_utils import get_genome_data as _get_genome_data
from disease.files_utils import get_genome_dirpath
from disease.files_utils import get_genome_filepath
from .models import CustomizedTag
from .forms import UploadGenomeForm
from .models import AnalyzeDataOrder
from .models import AlleleColor
from .models import SNPMarker
from .models import SNPMarkerArticle
from .tasks import recompute_genome_file

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


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        return context


class UploadGenome(GenomeFilePathMixin, FormView):
    template_name = 'upload_genome.html'
    form_class = UploadGenomeForm
    # success_url = reverse_lazy('disease:upload_success')

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

    def get_success_url(self):
        return reverse_lazy('disease:upload_success', kwargs={'pk': self.analyze_order_pk})

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
        task_id = celery_uuid()
        analyze_order = AnalyzeDataOrder(uploaded_filename=raw_filename, user=user, task_uuid=task_id)

        if user.is_staff and user.is_active:
            log.info('User %s skipping payment due to staff membership', user)
            analyze_order.paid = timezone.now()
        analyze_order.save()
        recompute_genome_file.apply_async(args=(self.get_filepath(raw_filename, user=user),),
                                          task_id=task_id)
        # table = process_genoome_data(data)
        # file_exists = os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.get_filepath(self.process_filename(raw_filename, filename_suffix='_processed'))))
        # if self.request.user.is_authenticated() and not file_exists:
        #     self.save_processed_data(table)

        # ctx = self.get_context_data(form=form, table=table, analyzed=True)
        self.analyze_order_pk = analyze_order.pk
        return super().form_valid(form)


def allele_description(request, pk):
    """
    login_required
    user should be able to view only his files
    """
    allele = request.GET['allele']
    marker = get_object_or_404(SNPMarker, pk=pk)
    try:
        article = get_object_or_404(SNPMarkerArticle, snp_marker=marker)
    except Http404:
        return redirect(marker.link)
    colours = AlleleColor.objects.filter(snp_marker=marker)
    your_allele = colours.get(allele=allele)
    ctx = {
        'marker': marker,
        'article': article,
        'colors': colours,
        'your_allele': your_allele,
        'base_template': 'base.html',
    }
    if 'ajax' in request.REQUEST:
        ctx['base_template'] = 'allele_ajax.html'
    return render(request, 'allele_description.html', ctx)


class UploadGenomeSuccessView(TemplateView):
    template_name = 'upload_success.html'

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.analyze_data_order = AnalyzeDataOrder.objects.get(pk=kwargs['pk'])
        user = request.user
        if self.analyze_data_order.is_paid or (user.is_staff and user.is_active):
            return redirect('{}?file={}'.format(reverse_lazy('disease:browse_genome'),
                                                self.analyze_data_order.uploaded_filename))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update(dict(bitpay_checkout_url=settings.BITPAY_API,
                           analyze_order=self.analyze_data_order,
                           paypal_form=PayPalPaymentsForm(
                               initial=self.analyze_data_order.paypal_data(self.request))
                           ))
        return super().get_context_data(**kwargs)


class DisplayGenomeResult(JSONResponseMixin, GenomeFilePathMixin, TemplateView):
    template_name = 'display_genome_result.html'

    def get(self, request, *args, **kwargs):
        self.user = self.request.user
        if self.is_browsing_via_admin:
            self.user = get_user_model().objects.get(pk=int(self.request.GET['pk']))
        return super().get(request, *args, **kwargs)

    def get_genome_data(self):
        filename = self.process_filename(self.request.GET['file'], filename_suffix='_processed')
        filepath = self.get_filepath(filename)
        data = _get_genome_data(filepath)
        data = list(reversed(sorted(data, key=lambda r: r.get('priority', -1))))
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

    def get_analyze_data_order(self):
        order_kwargs = dict(uploaded_filename=self.request.GET['file'], user=self.user)
        try:
            analyze_data_order = AnalyzeDataOrder.objects.get(**order_kwargs)
        except AnalyzeDataOrder.DoesNotExist:
            if not self.is_browsing_via_admin:
                analyze_data_order = AnalyzeDataOrder(**order_kwargs)
                analyze_data_order.save()
        return analyze_data_order

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['allele_tags'] = CustomizedTag.objects.filter(show_on_data=True)
        ctx['is_admin'] = is_admin = self.is_admin

        analyze_data_order = self.get_analyze_data_order()
        paid = analyze_data_order.is_paid

        job = AsyncResult(analyze_data_order.task_uuid)
        ctx['genome_data_url'] = '{}?file={}'.format(reverse_lazy('disease:browse_genome'), self.request.GET['file'])
        if self.is_browsing_via_admin:
            ctx['genome_data_url'] += '&pk={}'.format(self.user.pk)

        ctx['is_job_ready'] = is_job_ready = job.ready()
        ctx['is_job_successful'] = is_job_successful = job.successful()
        ctx['is_job_failure'] = is_job_failure = job.failed()
        if is_job_ready and is_job_successful:
            ctx['paid'] = paid
            if paid or is_admin:
                ctx['table'] = self.get_genome_data()
            ctx['bitpay_checkout_url'] = settings.BITPAY_API
            ctx['analyze_order'] = analyze_data_order
            ctx['pos_data'] = analyze_data_order.posData()
            ctx['paypal_form'] = PayPalPaymentsForm(
                initial=analyze_data_order.paypal_data(self.request))
        elif is_job_ready and is_job_failure:
            if not self.request.is_ajax():
                messages.add_message(self.request, settings.DANGER, "An error occured while processing your genome data. Please contact us for details.")
        else:
            if not self.request.is_ajax():
                messages.add_message(self.request, messages.INFO, 'Your genome data is being analyzed. Wait a few second and try this page again')


        return ctx

    def get_data(self, context):
        analyze_data_order = self.get_analyze_data_order()
        if analyze_data_order is not None:
            paid = analyze_data_order.is_paid

        result = []
        job = AsyncResult(analyze_data_order.task_uuid)
        if paid or self.is_admin:
            result = self.get_genome_data()
        return {
            'data': result,
            'is_ready': job.ready(),
        }

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            return self.render_to_json_response(context)
        else:
            return super().render_to_response(context, **response_kwargs)


def landing_genome_data(request):
    sample_data_filepath = 'disease/samplegenotype'
    data = {'data': _get_genome_data(sample_data_filepath)}
    data['data'] = list(reversed(sorted(data['data'], key=lambda r: r.get('priority', -1))))
    return JsonResponse(data)


class PaymentStatusView(ProcessFormView, TemplateView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        post_data = self.request.POST
        if post_data['status'] in {'paid', 'complete', 'confirmed'}:
            posData = json.loads(post_data['posData'])
            analyze_order_pk = posData['analyze_order_pk']
            user_pk = posData['user_pk']

            analyze_order = AnalyzeDataOrder.objects.get(pk=analyze_order_pk)
            analyze_order.paid = timezone.now()
            analyze_order.save()
        return HttpResponse('OK')
