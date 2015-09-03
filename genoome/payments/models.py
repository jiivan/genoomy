#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from coupons.models import Coupon

class CouponRedeemed(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    coupon = models.ForeignKey(Coupon)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'coupon',),)