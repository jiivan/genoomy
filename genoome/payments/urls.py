from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
import payments.signals  # noqa

from . import views

urlpatterns = [
    url(r'^paypal-callback/', include('paypal.standard.ipn.urls'),
        name='paypal_callback'),
    url(r'^redeem_coupon/$', login_required(views.CouponPaymentView.as_view()), name='redeem_coupon'),
]
