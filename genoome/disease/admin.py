from django.contrib import admin
from django import forms
from django.core.urlresolvers import reverse
from django.utils.html import format_html_join
from django_markdown.widgets import AdminMarkdownWidget

from .models import AlleleColor, SNPMarker, AnalyzeDataOrder, SNPMarkerArticle, CustomizedTag


class SNPMarkerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'rsid', 'risk_allele', 'link', 'p_value', 'or_or_beta', 'disease_trait')
    search_fields = ('rsid', 'risk_allele', 'p_value', 'or_or_beta', 'disease_trait')
    ordering = ('rsid',)


class AlleleColorAdminForm(forms.ModelForm):
    description = forms.CharField(widget=AdminMarkdownWidget)
    short_description = forms.CharField(widget=AdminMarkdownWidget)


class AlleleColorAdmin(admin.ModelAdmin):
    list_display = ('allele', 'color_alias',  'priority', 'snp_marker', 'short_description', )
    readonly_fields = ('snp_articles',)
    raw_id_fields = ("snp_marker",)
    search_fields = ('allele',)
    list_filter = ('allele',)
    form = AlleleColorAdminForm

    def snp_articles(self, instance):
        article_links = []
        for article in instance.snp_marker.snp_article.all():
            article_class = article.__class__
            url = reverse('admin:{}_{}_change'.format(article._meta.app_label, article._meta.model_name),
                          args=(article.pk,))
            article_links.append((url, article.title,))
        return format_html_join(' | ', '<a href="{}">{}</a>', ((url, alias,) for url, alias in article_links))
    snp_articles.allow_tags = True




class SNPMarkerArticleAdmin(admin.ModelAdmin):
    list_display = ('snp_marker', 'title', 'gene_area', 'variant',)
    readonly_fields = ('variant',)
    raw_id_fields = ("snp_marker",)

    def variant(self, instance):
        color_links = []
        for variant in instance.snp_marker.allele_colors.all():
            variant_model = variant.__class__
            url = reverse('admin:{}_{}_change'.format(variant_model._meta.app_label, variant_model._meta.model_name),
                          args=(variant.pk,))
            color_links.append((url, variant.__str__(),))
        return format_html_join(' | ', '<a href="{}">{}</a>', ((url, alias,) for url, alias in color_links))
    variant.allow_tags = True

class AnalyzeDataOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_filename', 'paid', 'task_uuid')
    search_fields = ('user', 'uploaded_filename')

class CustomizedTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_off', 'color_on', 'show_on_data', 'show_on_landing')

admin.site.register(CustomizedTag, CustomizedTagAdmin)
admin.site.register(SNPMarker, SNPMarkerAdmin)
admin.site.register(SNPMarkerArticle, SNPMarkerArticleAdmin)
admin.site.register(AlleleColor, AlleleColorAdmin)
admin.site.register(AnalyzeDataOrder, AnalyzeDataOrderAdmin)