#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.utils import timezone

from coupons.forms import CouponForm
from coupons.models import Coupon
from disease.models import AnalyzeDataOrder
from payments.models import CouponRedeemed

class CouponPaymentForm(CouponForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.analyze_data_order = AnalyzeDataOrder.objects.get(pk=int(self.request.GET['order_id']))
        super().__init__(*args, **kwargs)

    def clean_code(self):
        coupon_val = super().clean_code()
        coupon = Coupon.objects.get(code=coupon_val)
        if CouponRedeemed.objects.filter(user=self.analyze_data_order.user,
                                         coupon=coupon).exists():
            raise forms.ValidationError('This coupon is already redeemed')
        return coupon_val

    def unlock_file(self):
        self.analyze_data_order.paid = timezone.now()
        self.analyze_data_order.save()
        coupon = coupon = Coupon.objects.get(code=self.cleaned_data['code'])
        coupon_redeemed = CouponRedeemed(user=self.analyze_data_order.user, coupon=coupon)
        coupon_redeemed.save()
