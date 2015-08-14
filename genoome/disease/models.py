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

    def __str__(self):
        return '{} - {} - {}'.format(self.rsid, self.risk_allele, self.disease_trait)

class AlleleColor(models.Model):
    priority = models.PositiveIntegerField(default=100)
    color = RGBColorField()
    allele = models.CharField(max_length=128)
    snp_marker = models.ForeignKey(SNPMarker, related_name='allele_colors')

    def __str__(self):
        return self.color
