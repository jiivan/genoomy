from django.conf.urls import url, include
import payments.signals  # noqa


urlpatterns = [
    url(r'^paypal-callback/', include('paypal.standard.ipn.urls'),
        name='paypal_callback'),
]
