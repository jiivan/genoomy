from io import BytesIO
import logging
import uuid
import pickle
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponseServerError
from django.views.generic import FormView
from django.views.generic import TemplateView

from .files_utils import parse_raw_genome_file
from .files_utils import process_genoome_data
from .files_utils import process_filename
from .files_utils import get_genome_dirpath
from .files_utils import get_genome_filepath
from .forms import UploadGenomeForm

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

    def get_dirpath(self):
        return get_genome_dirpath(self.request.user)

    def get_filepath(self, filename):
        return get_genome_filepath(self.request.user, filename)

class UploadGenome(GenomeFilePathMixin, FormView):
    template_name = 'upload_genome.html'
    form_class = UploadGenomeForm

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
        data = parse_raw_genome_file(self.request.FILES['file'])
        raw_filename = self.request.FILES['file'].name
        storage.save(self.get_filepath(raw_filename), self.request.FILES['file'])
        table = process_genoome_data(data)
        file_exists = os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.get_filepath(self.process_filename(raw_filename, filename_suffix='_processed'))))
        if self.request.user.is_authenticated() and not file_exists:
            self.save_processed_data(table)

        ctx = self.get_context_data(form=form, table=table, analyzed=True)
        return self.render_to_response(ctx)


class DisplayGenomeResult(GenomeFilePathMixin, TemplateView):
    template_name = 'display_genome_result.html'

    def get_genome_data(self):
        filename = self.process_filename(self.request.GET['file'], filename_suffix='_processed')
        filepath = self.get_filepath(filename)
        with storage.open(filepath) as f:
            data = pickle.load(f)
        return data

    def is_browsing_via_admin(self):
        return bool(('pk' in self.request.GET) and self.request.user.is_staff and self.request.user.is_active)

    def get_filepath(self, filename):
        if self.is_browsing_via_admin():
            user = get_user_model().objects.get(pk=int(self.request.GET['pk']))
            return get_genome_filepath(user, filename)
        return super().get_filepath(filename)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['table'] = self.get_genome_data()
        if self.is_browsing_via_admin():
            ctx['is_admin'] = True
        return ctx