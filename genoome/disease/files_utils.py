#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from django.utils.encoding import force_str

from disease.models import SNPMarker

log = logging.getLogger(__name__)

def parse_raw_genome_file_gen(file):
    RSID = 0
    GENOTYPE = 3
    POSITION = 2
    for line in file:
        line = force_str(line)
        if line.startswith('#'):
            continue
        l = line.strip().split('\t')
        if not l[RSID].startswith('rs'):
            continue
        rsid = l[RSID].replace('rs', '', 1)
        yield rsid, {'genotype': l[GENOTYPE], 'position': l[POSITION]}


def parse_raw_genome_file(file):
    data = {}
    for rsid, line in parse_raw_genome_file_gen(file):
        data[rsid] = line
    return data


def process_genoome_data_gen(data):
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

        yield row
    log.debug('PID: %s, MARKERS PROCESSED', os.getpid())


def process_genoome_data(data):
    table = []
    for row in process_genoome_data_gen(data):
        table.append(row)
    return table


def process_filename(filename, filename_suffix=None):
    if filename_suffix is not None:
        filename, ext = filename.rsplit('.', 1)
        filename = '{}{}.{}'.format(filename, filename_suffix, ext)
    return filename


def get_genome_dirpath(user):
    app_dir = 'disease'
    user_subdir = '{}:{}'.format(user.pk, user.email)
    return os.path.join(app_dir, user_subdir)


def get_genome_filepath(user, filename):
    return os.path.join(get_genome_dirpath(user), filename)