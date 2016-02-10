from celery import shared_task
from celery import uuid as celery_uuid
import csv
import datetime
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
import logging
import requests
import time

from disease.files_utils import get_genome_filepath
from disease.tasks import recompute_genome_file
from twentythree.models import CeleryTask23
from twentythree.models import Token23

log = logging.getLogger('genoome.twentythree.tasks')

def twentythree_snp_mapping():
    snp_path = settings.SNP_MAPPING_FILEPATH23

    if not os.path.exists(snp_path):
        log.warning('Fetching snps mapping from 23andme.com')
        response = requests.get('https://api.23andme.com/res/txt/snps.b4e00fe1db50.data')
        with open(snp_path, 'w') as f:
            f.write(response.text)
        log.warning('New snps mapping23 saved at: %s', snp_path)

    with open(snp_path) as snp_mapping_f:
        csv_reader = csv.reader(snp_mapping_f)
        for row in csv_reader:
            index, rsid, chromosome, position = row
            index = int(index)
            yield index*2, rsid, chromosome, position

@shared_task
def fetch_genome_and_push_forward(ctask_pk):
    ctask = CeleryTask23.objects.get(pk=ctask_pk)
    ctask.status = 'fetching'
    ctask.save()
    def _may_raise():
        user_pk = ctask.user_id
        profile_id = ctask.chosen_profile

        filename = 'twentythree_%s_%s_%s.csv' % (user_pk, slugify(profile_id), int(time.time()))
        filepath = get_genome_filepath(ctask.user, filename)

        from django.core.files.storage import FileSystemStorage
        storage = FileSystemStorage()
        token = Token23.objects.get(user_id=user_pk)
        try:
            genome = token.get_genome(profile_id)
        except Token23.ClientError as e:
            if e.json()['error'] == 'access_denied':
                log.warning('Got access_denied. Refreshing token:%s', token.pk)
                token.refresh()
            else:
                raise

        with storage.open(filepath, 'w') as csv_file:
            csv_file.write('# 23andme\n') # for disease.files_utils.get_parser() to detect 23andme format
            csv_file.write('# generated by twentythree at UTC %s\n' % (datetime.datetime.utcnow(),))
            csv_file.write('# fetched from api\n')
            csv_writer = csv.writer(csv_file)
            for index, rsid, chromosome, position in twentythree_snp_mapping():
                if not rsid.startswith('rs'):
                    continue
                genotype = genome[index:index+1]
                csv_writer.writerow([rsid, chromosome, position, genotype])

        task_id = celery_uuid()
        analyze_order = AnalyzeDataOrder.objects.create(uploaded_filename=filename, user_id=user_pk, task_uuid=task_id)
        ctask.analyze_order = analyze_order
        ctask.status = 'parsing'
        ctask.save()
        recompute_genome_file.apply_async(args=(filepath,), task_id=task_id)
    try:
        _may_raise()
    except Exception as e:
        log.exception('Problem running fetch_genome_and_push_forward().')
        ctask.status = 'error'
        ctask.save()
        raise
