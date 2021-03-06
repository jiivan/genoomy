from celery import shared_task
from celery import uuid as celery_uuid
import csv
import datetime
from django.conf import settings
import django.core.files
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
import logging
import os.path
import requests
import tempfile
import time

from disease.files_utils import get_genome_filepath
from disease.models import AnalyzeDataOrder
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
        csv_reader = csv.reader(snp_mapping_f, delimiter='\t')
        for row in csv_reader:
            if len(row) == 1:
                log.debug('Ignoring: %r', row)
                continue
            index, rsid, chromosome, position = row
            if not index.isdigit():
                log.debug('idx notdigit. Inoring: %r', row)
                continue
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
        log.info('Fetching genome...')
        try:
            genome = token.get_genome(profile_id)
            log.info('Got genome len(%d)', len(genome))
        except Token23.ClientError as e:
            if e.json()['error'] == 'access_denied':
                log.warning('Got access_denied. Refreshing token:%s', token.pk)
                token.refresh()
            else:
                raise

        with tempfile.TemporaryFile('w+') as csv_file:
            log.info('Formatting csv for tempfile')
            csv_file.write('# 23andme\n') # for disease.files_utils.get_parser() to detect 23andme format
            csv_file.write('# generated by twentythree at UTC %s\n' % (datetime.datetime.utcnow(),))
            csv_file.write('# fetched from api\n')
            csv_writer = csv.writer(csv_file, delimiter='\t')
            for index, rsid, chromosome, position in twentythree_snp_mapping():
                #log.debug('index: %r rsid: %r chromosome: %r position: %s', index, rsid, chromosome, position)
                if not rsid.startswith('rs'):
                    #log.debug('ignoring: %r', rsid)
                    continue
                genotype = genome[index:index+2]
                #log.debug('genotype: %r', genotype)
                csv_writer.writerow([rsid, chromosome, position, genotype])
            log.info('Saving csv to storage...')
            storage.save(filepath, django.core.files.File(csv_file))

        task_id = celery_uuid()
        analyze_order = AnalyzeDataOrder.objects.create(uploaded_filename=filename, user_id=user_pk, task_uuid=task_id)
        ctask.analyze_order = analyze_order
        ctask.status = 'parsing'
        ctask.save()
        log.info('Calling recompute_genome_file...')
        recompute_genome_file.apply_async(args=(filepath,), task_id=task_id)
        log.debug('Done.')
    try:
        _may_raise()
    except Exception as e:
        log.exception('Problem running fetch_genome_and_push_forward().')
        ctask.status = 'error'
        ctask.save()
        raise
