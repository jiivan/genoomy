#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView

from .forms import CouponPaymentForm

class CouponPaymentView(FormView):
    form_class = CouponPaymentForm
    template_name = 'redeem_coupon.html'

    def dispatch(self, request, *args, **kwargs):
        self.analyze_data_order_pk = request.GET['order_id']
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        form = self.get_form()
        return self.render_to_response(self.get_context_data(form=form,
                                                             analyze_data_order_pk=self.analyze_data_order_pk))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form,
                                                             analyze_data_order_pk=self.analyze_data_order_pk))

    def get_success_url(self):
        return reverse_lazy('disease:upload_success', kwargs={'pk': self.analyze_data_order_pk})

    def form_valid(self, form):
        form.unlock_file()
        return super().form_valid(form)