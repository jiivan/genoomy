from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from disease.models import AnalyzeDataOrder
from django.utils import timezone
import logging

log = logging.getLogger(__name__)


def paypal_callback(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        analyze_order_pk = ipn_obj.invoice
        try:
            analyze_order = AnalyzeDataOrder.objects.get(pk=analyze_order_pk)
            analyze_order.paid = timezone.now()
            analyze_order.save()
            log.info('Order %r paid by %r', analyze_order, ipn_obj)
        except AnalyzeDataOrder.DoesNotExist:
            log.warning('No order found for %r', ipn_obj)
    else:
        log.warning('Payment not completed yet: %r', ipn_obj)

valid_ipn_received.connect(paypal_callback)
