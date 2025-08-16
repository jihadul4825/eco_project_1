from django.shortcuts import render, redirect
from .models import Order,OrderProduct, Payment
from cart.models import Cart, CartItem
from store.models import Product
from category.models import Category
from .forms import OrderForm


from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime


def place_order(request, total=0, quantity=0):
    current_user = request.user
    #if the cart count is less than or equal to 0, then redirect back to store
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            form.instance.user = current_user
            form.instance.order_total = grand_total
            form.instance.tax = tax
            form.instance.ip = request.META.get('REMOTE_ADDR')
            saved_instance = form.save() # save the form data to the database
            saved_instance_id = saved_instance.id 
            # Genarate order number
            
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(saved_instance_id)
            
            form.instance.order_number = order_number
            form.save()
            # order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            # context = {
            #     'order':order,
            #     'cart_items':cart_items,
            #     'total':total,
            #     'tax':tax,
            #     'grand_total':grand_total,
            #     'order_number':order_number
            # }
            # return render(request, 'orders/payments.html', context)
            return redirect('checkout')
    else:
        return redirect('checkout')

            
            
            
            
            
            