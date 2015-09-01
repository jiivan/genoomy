from django.contrib.auth import get_user_model
from django.test import TestCase

from coupons.models import Coupon
from disease.forms import CouponPaymentForm
from disease.models import AnalyzeDataOrder
from payments.models import CouponRedeemed

class CouponPaymentFormTests(TestCase):

    def setUp(self):
        user = get_user_model().objects.create_user('test@test.com', 'test@test.com')
        AnalyzeDataOrder(user_id=user.pk, uploaded_filename='testfile.txt').save()
        Coupon.objects.create_coupon('monetary', 'test_coupon')

    def test_coupon_is_required(self):
        form = CouponPaymentForm()
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_errors('coupon', 'required'))
        analyze_data_order = AnalyzeDataOrder.objects.get(user_id=1)
        self.assertFalse(analyze_data_order.is_paid)
        self.assertRaises(CouponRedeemed.DoesNotExist,
                          CouponRedeemed.objects.get,
                          user_id=1, coupon_id=1)

    def test_wrong_coupon_sumbitted(self):
        data = {'coupon': 'wrong'}
        form = CouponPaymentForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_errors('coupon', 'invalid'))
        analyze_data_order = AnalyzeDataOrder.objects.get(user_id=1)
        self.assertFalse(analyze_data_order.is_paid)
        self.assertRaises(CouponRedeemed.DoesNotExist,
                          CouponRedeemed.objects.get,
                          user_id=1, coupon_id=1)

    def test_correct_coupon_submitted(self):
        data = {'coupon': 'test_coupon'}
        form = CouponPaymentForm(data)
        self.assertTrue(form.is_valid())
        analyze_data_order = AnalyzeDataOrder.objects.get(user_id=1)
        self.assertTrue(analyze_data_order.is_paid)
        self.assertTrue(CouponRedeemed.objects.filter(user_id=1, coupon_id=1).exists())