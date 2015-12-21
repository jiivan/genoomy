# -*- coding: utf-8 -*-

from django import template
from django.core.urlresolvers import reverse_lazy

from configurable_elements.models import get_legend_rows
from disease.models import CustomizedTag

register = template.Library()


@register.inclusion_tag('includes/data_table.html', takes_context=True)
def data_table(context):
    inner_context = {}
    inner_context['legend_rows'] = get_legend_rows()
    inner_context['allele_tags'] = CustomizedTag.objects.filter(show_on_landing=True)
    inner_context['genome_data_url'] = reverse_lazy('disease:landing_json_data')
    return inner_context
