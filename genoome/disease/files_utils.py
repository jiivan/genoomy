#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import logging
import os
import zipfile

from disease.models import SNPMarker

log = logging.getLogger(__name__)

def parse_ancestrydna(file):
    RSID = 0
    ALLELE1 = 3
    ALLELE2 = 4
    POSITION = 2
    COLUMNS = ['rsid', 'chromosome', 'position', 'allele1', 'allele2']
    for line in file:
        if len(line) == 1:
            continue
        if line == COLUMNS:
            continue
        if not line[RSID].startswith('rs'):
            continue
        rsid = line[RSID].replace('rs', '', 1)
        genotype = ''.join((line[ALLELE1], line[ALLELE2]))
        yield rsid, {'genotype': genotype, 'position': line[POSITION]}


def parse_23andme(file):
    RSID = 0
    GENOTYPE = 3
    POSITION = 2
    for line in file:
        if len(line) == 1:
            continue
        if not line[RSID].startswith('rs'):
            continue
        rsid = line[RSID].replace('rs', '', 1)
        yield rsid, {'genotype': line[GENOTYPE], 'position': line[POSITION]}


parsers = {'23andme': parse_23andme,
           'ancestrydna': parse_ancestrydna}

def get_parser(file):
    choosen_parser = None
    break_outer = False
    for line in file:
        for key, parser in parsers.items():
            if key in line.lower():
                choosen_parser = parser
                log.debug('%s file detected, chosing apropriate parser', key)
                break_outer = True
                break
        if break_outer:
            break

    file.seek(0, 0)
    if choosen_parser is None:
        raise ValueError('Cannot determine file format')
    return choosen_parser


def parse_raw_genome_file_gen(file):
    parser = get_parser(file)
    reader = csv.reader(file, delimiter='\t')
    return parser(reader)


def parse_raw_genome_file(file):
    data = {}
    log.debug('PID: %s, PARSING GENOME FILE STARTED', os.getpid())
    for rsid, line in parse_raw_genome_file_gen(file):
        data[rsid] = line
    log.debug('PID: %s, PARSING GENOME FILE FINISHED', os.getpid())
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


def handle_zipped_genome_file(genome_file):
    parsed_file = None

    with zipfile.ZipFile(genome_file) as zipped_file:
        # Check if archive contains .txt file with the same filename as archive
        namelist = zipped_file.namelist()
        for unzipped_full_filename in namelist:
            with zipped_file.open(unzipped_full_filename) as unzipped_file:
                parsed_file = parse_raw_genome_file(unzipped_file)
                break

    if parsed_file is None:
        log.error('No valid genome files found: %s in archive', namelist)
        raise KeyError('There is no valid genome file in the archive')
    return parsed_file