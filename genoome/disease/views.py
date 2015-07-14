import json
import uuid

from django.core.cache import cache
from django.http import JsonResponse, HttpResponseServerError
from django.views.generic import FormView
from django.utils.encoding import force_str

from .forms import UploadGenomeForm
from .models import SNPMarker

def parse_raw_genome_file(file):
    RSID = 0
    GENOTYPE = 3
    data = {}
    for line in file:
        line = force_str(line)
        if line.startswith('#'):
            continue
        l = line.strip().split('\t')
        if not l[RSID].startswith('rs'):
            continue
        rsid = l[RSID].replace('rs', '', 1)
        data[rsid] = l[GENOTYPE]
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
        if data is None:
            data = {'length': 1, 'uploaded': 1}
        return JsonResponse(data)
    else:
        return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')

class UploadGenome(FormView):
    template_name = 'upload_genome.html'
    form_class = UploadGenomeForm

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        form = self.get_form()
        upload_id = uuid.uuid4()
        return self.render_to_response(self.get_context_data(form=form, upload_id=upload_id))


    def form_valid(self, form):
        data = parse_raw_genome_file(self.request.FILES['file'])
        # markers = SNPMarker.objects.filter(rsid__in=data.keys())
        table = []
        print('PROCESING MARKERS')
        for marker in SNPMarker.objects.filter(rsid__in=data.keys()).iterator():
            mrsid = str(marker.rsid)
            if mrsid not in data:
                continue
            row = {'rsid': mrsid,
             'risk_allele': marker.risk_allele,
             'disease_trait': marker.disease_trait,
             'p_value': marker.p_value,
             'or_or_beta': marker.or_or_beta,
             'genotype': data[mrsid],
             'risk': bool(marker.risk_allele in data[mrsid])
             }
            table.append(row)
        print('MARKERS PROCESSED')

        ctx = self.get_context_data(form=form, table=table, analyzed=True)
        return self.render_to_response(ctx)
