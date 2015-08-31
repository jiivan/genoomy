from django.contrib import admin

from .models import AlleleColor, SNPMarker, AnalyzeDataOrder

class SNPMarkerAdmin(admin.ModelAdmin):
    list_display = ('rsid', 'risk_allele', 'p_value', 'or_or_beta', 'disease_trait')
    search_fields = ('rsid', 'risk_allele', 'p_value', 'or_or_beta', 'disease_trait')
    ordering = ('rsid',)


class AlleleColorAdmin(admin.ModelAdmin):
    list_display = ('allele', 'color', 'snp_marker')
    raw_id_fields = ("snp_marker",)


class AnalyzeDataOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_filename', 'paid')
    search_fields = ('user', 'uploaded_filename')


admin.site.register(SNPMarker, SNPMarkerAdmin)
admin.site.register(AlleleColor, AlleleColorAdmin)
admin.site.register(AnalyzeDataOrder, AnalyzeDataOrderAdmin)