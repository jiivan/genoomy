from django.contrib import admin
from django import forms
from django_markdown.widgets import AdminMarkdownWidget

from .models import AlleleColor, SNPMarker, AnalyzeDataOrder, SNPMarkerArticle

class SNPMarkerAdmin(admin.ModelAdmin):
    list_display = ('rsid', 'risk_allele', 'link', 'p_value', 'or_or_beta', 'disease_trait')
    search_fields = ('rsid', 'risk_allele', 'p_value', 'or_or_beta', 'disease_trait')
    ordering = ('rsid',)


class AlleleColorAdminForm(forms.ModelForm):
    description = forms.CharField(widget=AdminMarkdownWidget)


class AlleleColorAdmin(admin.ModelAdmin):
    list_display = ('allele', 'color', 'color_alias',  'priority', 'snp_marker')
    raw_id_fields = ("snp_marker",)
    search_fields = ('allele',)
    list_filter = ('allele',)
    form = AlleleColorAdminForm


class SNPMarkerArticleAdmin(admin.ModelAdmin):
    list_display = ('snp_marker', 'title')
    raw_id_fields = ("snp_marker",)


class AnalyzeDataOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_filename', 'paid')
    search_fields = ('user', 'uploaded_filename')


admin.site.register(SNPMarker, SNPMarkerAdmin)
admin.site.register(SNPMarkerArticle, SNPMarkerArticleAdmin)
admin.site.register(AlleleColor, AlleleColorAdmin)
admin.site.register(AnalyzeDataOrder, AnalyzeDataOrderAdmin)