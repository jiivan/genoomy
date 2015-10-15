import json

from colorful.fields import RGBColorField
from django.contrib.sites.models import Site
from django.conf import settings
from django.db import models
from django.utils import timezone, http
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, resolve, Resolver404
from django_markdown.models import MarkdownField

from color_aliases.models import ColorAlias
from taggit.managers import TaggableManager
from taggit.models import GenericTaggedItemBase
from taggit.models import TagBase

class SNPMarker(models.Model):
    rsid = models.BigIntegerField()
    link = models.TextField()
    risk_allele = models.CharField(max_length=128)
    disease_trait = models.TextField()
    comment = models.TextField()
    p_value = models.FloatField(blank=True, null=True)
    or_or_beta = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = 'Trai'

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


class CustomizedTag(TagBase):
    color_off = RGBColorField()
    color_on = RGBColorField()
    show_on_data = models.BooleanField(default=True)
    show_on_landing = models.BooleanField(default=True)
    image = models.ImageField(upload_to='tags/')

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class TaggedWhatever(GenericTaggedItemBase):
    tag = models.ForeignKey(CustomizedTag,
                            related_name="%(app_label)s_%(class)s_items")


class AlleleColor(models.Model):
    priority = models.PositiveIntegerField(default=100)
    color_alias = models.ForeignKey(ColorAlias, default=1)
    allele = models.CharField(max_length=128)
    description = MarkdownField()
    snp_marker = models.ForeignKey(SNPMarker, related_name='allele_colors')
    tags = TaggableManager(through=TaggedWhatever)

    class Meta:
        verbose_name = 'Variant'

    def __str__(self):
        return self.color_alias.alias


class SNPMarkerArticle(models.Model):
    snp_marker = models.ForeignKey(SNPMarker, related_name='snp_article')
    title = models.CharField(max_length=128, help_text='Title for SNM description page')
    gene_area = models.CharField(max_length=256, blank=True, null=True)
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
