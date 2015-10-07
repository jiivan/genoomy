from datetime import datetime
import json

from colorful.fields import RGBColorField
from django.contrib.sites.models import Site
from django.conf import settings
from django.db import models
from django.utils import timezone, http
from django.core.urlresolvers import reverse, resolve, Resolver404
from django_markdown.models import MarkdownField

from color_aliases.models import ColorAlias

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

    def get_absolute_url(self):
        """
        If url is not from our
        """
        url = reverse('disease:description', kwargs={'pk': self.pk})
        # link = self.link
        # url_info = http.urlparse(link)
        # try:
        #     resolve(url_info.path)
        # except Resolver404:
        #     url = link
        return url


class AlleleColor(models.Model):
    priority = models.PositiveIntegerField(default=100)
    color = RGBColorField()
    color_alias = models.ForeignKey(ColorAlias, default=1)
    allele = models.CharField(max_length=128)
    description = MarkdownField()
    snp_marker = models.ForeignKey(SNPMarker, related_name='allele_colors')

    def __str__(self):
        return self.color


class SNPMarkerArticle(models.Model):
    snp_marker = models.ForeignKey(SNPMarker, related_name='snp_article')
    title = models.CharField(max_length=128, help_text='Title for SNM description page')
    header = MarkdownField(help_text='Introductory text appearing in header section of SNP description')
    footer = MarkdownField(help_text='Place for footer, bibliography etc.')


class AnalyzeDataOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    uploaded_filename = models.CharField(max_length=256)
    paid = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return 'User: {} Payment: {} For: {}'.format(self.user, self.paid, self.uploaded_filename)

    class Meta:
        unique_together = (('user', 'uploaded_filename'),)

    def posData(self):
        return json.dumps({'analyze_order_pk': self.pk, 'user_pk': self.user.pk})

    def paypal_data(self, request):
        return {
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "amount": "19.00",  # TODO move to settings
            "item_name": "Genoomy analysis",
            "invoice": self.id,
            "notify_url": request.build_absolute_uri(reverse('payments:paypal-ipn')),

            # TODO add informative flashes
            "return_url": request.build_absolute_uri(
                reverse('disease:upload_success', kwargs={'pk': self.pk})),
            "cancel_return": request.build_absolute_uri(
                reverse('disease:upload_success', kwargs={'pk': self.pk})),
            }

    @property
    def is_paid(self):
        return bool(self.paid and self.paid < timezone.now())
