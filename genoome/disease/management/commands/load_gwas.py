#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from django.core.management.base import BaseCommand, CommandError
import psycopg2

from disease.models import SNPMarker

def map_SNP_model_fields(gwas_dict):

    def clean_NR(value):
        if value in {'NR', 'NS'}:
            value = None
        return value

    def handle_precision_overflow(value):
        if value is None:
            return value
        try:
            fvalue = float(value)
        except ValueError:
            return None
        return round(fvalue, 308)

    snp_kwargs = {
        'rsid': gwas_dict['strongest_snp'],
        'link': gwas_dict['link'],
        'risk_allele': gwas_dict['risk_allele'],
        'disease_trait': gwas_dict['disease_trait'],
        'p_value': handle_precision_overflow(clean_NR(gwas_dict['p_value'])),  # Hacks for double precision overflow in Postgres
        'or_or_beta': handle_precision_overflow(clean_NR(gwas_dict['or_or_beta']))
    }
    return snp_kwargs


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('args', metavar='gwas', nargs='+')

    def handle(self, *args, **options):
        self.stdout.write('Args: {}'.format(args))
        for file in args:
            with open(file, 'r') as f:
                for entry in json.load(f):
                    snp_fields = map_SNP_model_fields(entry)
                    self.stdout.write('PROCESSING SNP: {}'.format(snp_fields))
                    # if entry['strongest_snp'].isdigit() in {'NR', 'HLA', 'APOE'}:
                    if not entry['strongest_snp'].isdigit():
                        self.stdout.write('Skipping entry with nonnumeric rsid')
                        continue
                    if SNPMarker.objects.filter(**snp_fields).exists():
                        self.stdout.write('Skipping duplicated entry')
                        continue
                    s = SNPMarker(**snp_fields)
                    s.full_clean()
                    try:
                        s.save()
                        self.stdout.write('SAVED SNP ENTRY')
                    except psycopg2.DataError as e:  # Double precision value overflow
                        self.stdout.write(e)
                        continue






