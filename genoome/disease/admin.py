from django.contrib import admin

from .models import SNPMarker

class SNPMarkerAdmin(admin.ModelAdmin):
    list_display = ('rsid', 'risk_allele', 'p_value', 'or_or_beta', 'disease_trait')
    search_fields = ('rsid', 'risk_allele', 'p_value', 'or_or_beta', 'disease_trait')
    ordering = ('rsid',)


admin.site.register(SNPMarker, SNPMarkerAdmin)