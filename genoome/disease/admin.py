from django.contrib import admin

from .models import AlleleColor, SNPMarker

class SNPMarkerAdmin(admin.ModelAdmin):
    list_display = ('rsid', 'risk_allele', 'p_value', 'or_or_beta', 'disease_trait')
    search_fields = ('rsid', 'risk_allele', 'p_value', 'or_or_beta', 'disease_trait')
    ordering = ('rsid',)

class AlleleColorAdmin(admin.ModelAdmin):
    list_display = ('allele', 'color')


admin.site.register(SNPMarker, SNPMarkerAdmin)
admin.site.register(AlleleColor, AlleleColorAdmin)