# import string
# import random
# from django.contrib.auth.decorators import login_required  
# from sslcommerz_lib import SSLCOMMERZ
# from .models import PaymentGateWaySettings
# from django.urls import reverse


# def unique_transaction_id_generator(size=10, chars=string.ascii_uppercase + string.digits):
#     return ''.join(random.choice(chars) for _ in range(size))


# @login_required
# def sslcommerz_payment_gateway(request, order_id, user_id, grand_total):
#     gateway_auth_details = PaymentGateWaySettings.objects.first()
#     settings = {
#         'store_id': gateway_auth_details.store_id,
#         'store_pass': gateway_auth_details.store_pass,
#         'issandbox': True
#     }

#     sslcommerz = SSLCOMMERZ(settings)
    
#     # Build callback URLs
#     success_url = request.build_absolute_uri(reverse('success'))
#     fail_url = request.build_absolute_uri(reverse('fail'))
#     cancel_url = request.build_absolute_uri(reverse('cancel'))
    
#     post_body = {
#         'total_amount': grand_total,
#         'currency': "BDT",
#         'tran_id': unique_transaction_id_generator(),
#         'success_url': success_url,
#         'fail_url': fail_url,
#         'cancel_url': cancel_url,
#         'emi_option': 0,

#         # real customer data
#         'cus_email': request.user.email,
#         'cus_phone': request.user.phone,
#         'cus_add1': request.user.address_line_1,
#         'cus_city': request.user.city,
#         'cus_country': 'Bangladesh',
#         'shipping_method': "NO",
#         'multi_card_name': "",
#         'num_of_item': 1,
#         'product_name': "Order Checkout",
#         'product_category': "E-commerce",
#         'product_profile': "general",

#         # pass IDs back to success_view
#         'value_a': str(order_id),   # order ID
#         'value_b': str(user_id),    # user ID
#         'value_c': request.user.email,
#     }

#     response = sslcommerz.createSession(post_body)
#     return 'https://sandbox.sslcommerz.com/gwprocess/v4/gw.php?Q=pay&SESSIONKEY=' + response
# ['sessionkey']

import string
import random
from django.contrib.auth.decorators import login_required  
from sslcommerz_lib import SSLCOMMERZ
from .models import PaymentGateWaySettings
from django.urls import reverse
from django.shortcuts import get_object_or_404
from orders.models import Order


def unique_transaction_id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@login_required
def sslcommerz_payment_gateway(request, order_id, user_id, grand_total):
    gateway_auth_details = PaymentGateWaySettings.objects.first()
    settings = {
        'store_id': gateway_auth_details.store_id,
        'store_pass': gateway_auth_details.store_pass,
        'issandbox': True
    }

    sslcommerz = SSLCOMMERZ(settings)
    
    # Get the order to access shipping information
    order = get_object_or_404(Order, id=order_id)
    
    # Build callback URLs
    success_url = request.build_absolute_uri(reverse('success'))
    fail_url = request.build_absolute_uri(reverse('fail'))
    cancel_url = request.build_absolute_uri(reverse('cancel'))
    
    post_body = {
        'total_amount': grand_total,
        'currency': "BDT",
        'tran_id': unique_transaction_id_generator(),
        'success_url': success_url,
        'fail_url': fail_url,
        'cancel_url': cancel_url,
        'emi_option': 0,

        # ✅ Use order information instead of user information for shipping details
        'cus_email': request.user.email,
        'cus_phone': order.phone,  # Use phone from order, not from user
        'cus_add1': order.address_line_1,
        'cus_city': order.city,
        'cus_country': order.country,

        'shipping_method': "NO",
        'product_name': "Order Checkout",
        'product_category': "E-commerce",
        'product_profile': "general",

        # ✅ pass IDs back to success_view
        'value_a': str(order_id),   # order ID
        'value_b': str(user_id),    # user ID
        'value_c': request.user.email,
    }

    response = sslcommerz.createSession(post_body)
    return 'https://sandbox.sslcommerz.com/gwprocess/v4/gw.php?Q=pay&SESSIONKEY=' + response['sessionkey']


