from io import BytesIO
import logging
import uuid
import pickle
import os

from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponseServerError
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.utils.encoding import force_str

from .forms import UploadGenomeForm
from .models import AlleleColor, SNPMarker

log = logging.getLogger(__name__)

storage = FileSystemStorage()

def parse_raw_genome_file(file):
    RSID = 0
    GENOTYPE = 3
    POSITION = 2
    data = {}
    for line in file:
        line = force_str(line)
        if line.startswith('#'):
            continue
        l = line.strip().split('\t')
        if not l[RSID].startswith('rs'):
            continue
        rsid = l[RSID].replace('rs', '', 1)
        data[rsid] = {'genotype': l[GENOTYPE], 'position': l[POSITION]}
    return data

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
        if filename_suffix is not None:
            filename, ext = filename.split('.')
            filename = '{}{}.{}'.format(filename, filename_suffix, ext)
        return filename

    def get_filepath(self, filename):
        app_dir = 'disease'
        user_subdir = '{}:{}'.format(self.request.user.pk, self.request.user.email)
        filename = filename
        return os.path.join(app_dir, user_subdir, filename)

class UploadGenome(GenomeFilePathMixin, FormView):
    template_name = 'upload_genome.html'
    form_class = UploadGenomeForm

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
        table = []
        log.debug('PID: %s, PROCESING MARKERS', os.getpid())
        markers = SNPMarker.objects.prefetch_related('allele_colors').filter(rsid__in=data.keys())
        for marker in markers:
            mrsid = str(marker.rsid)
            if mrsid not in data:
                continue

            row = {'rsid': mrsid,
                   'risk_allele': marker.risk_allele,
                   'chromosome_position': data[mrsid]['position'],
                   'disease_trait': marker.disease_trait,
                   'p_value': marker.p_value,
                   'or_or_beta': marker.or_or_beta,
                   'genotype': data[mrsid]['genotype'],
                   'risk': data[mrsid]['genotype'].count(marker.risk_allele),
                   'link': marker.link
                   }

            allele_colors = marker.allele_colors.all()
            for allele_color in allele_colors:
                if row['genotype'] == allele_color.allele:
                    row.update({'color': allele_color.color, 'priority': allele_color.priority})
                    break

            table.append(row)
        log.debug('PID: %s, MARKERS PROCESSED', os.getpid())

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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['table'] = self.get_genome_data()
        return ctx