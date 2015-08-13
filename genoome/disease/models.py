from colorful.fields import RGBColorField
from django.db import models


class SNPMarker(models.Model):
    rsid = models.BigIntegerField()
    link = models.TextField()
    risk_allele = models.CharField(max_length=128)
    disease_trait = models.TextField()
    comment = models.TextField()
    p_value = models.FloatField(blank=True, null=True)
    or_or_beta = models.FloatField(blank=True, null=True)

class AlleleColor(models.Model):
    color = RGBColorField()
    allele = models.CharField(max_length=128)
