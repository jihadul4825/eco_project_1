from django.urls import reverse
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.models import Account
from cart.models import CartItem
from store.models import Product
from .forms import OrderForm
from .models import Payment, OrderProduct, Order
from .ssl import sslcommerz_payment_gateway


@csrf_exempt
@transaction.atomic
def success_view(request):
    data = request.POST
    # print('data--------', data)
     # Extract values
    order_id = data.get('value_a')
    user_id = data.get('value_b')
    
    user = get_object_or_404(Account, pk=user_id)
    order = get_object_or_404(Order, pk=order_id, user=user, is_ordered=False)
    
    # Create Payment entry
    payment = Payment.objects.create(
        user=user,
        payment_id=data['tran_id'],
        payment_method=data['card_issuer'],
        amount_paid=data['store_amount'],
        status=data['status']
    )

    # Update order
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    # Move cart items to order products
    cart_items = CartItem.objects.select_related('product').filter(user=user)
    for item in cart_items:
        OrderProduct.objects.create(
            order=order,
            payment=payment,
            user=user,
            product=item.product,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True
        )
    
        # Reduce stock
        item.product.stock -= item.quantity
        item.product.save()
        # Clear cart
        item.delete()
  
    # Redirect with query parameters instead of URL parameters
    redirect_url = reverse('order_complete') + f'?order_number={order.order_number}&payment_id={payment.payment_id}'
    return redirect(redirect_url)


@login_required
def order_complete(request):
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')

    try:
        # Solve N+1 problem using select_related and prefetch_related
        order = Order.objects.select_related('user').prefetch_related('order_products__product').get(
            order_number=order_number, 
            is_ordered=True
        )

        payment = Payment.objects.get(payment_id=payment_id)

        # Get ordered products
        ordered_products = order.order_products.all()
        
        # Calculate subtotal, tax, and grand total
        subtotal = sum([product.product.price * product.quantity for product in ordered_products])
        tax = subtotal * 0.05  # Assuming 5% tax
        grand_total = subtotal + tax
        

        context = {
            'order': order,
            'payment': payment,
            'ordered_products': ordered_products,
            'subtotal': subtotal,
            'tax': tax,
            'grand_total': grand_total
        }
        return render(request, 'orders/order_complete.html', context)

    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('dashboard')



@login_required
def place_order(request):
    grand_total = 0
    tax = 0
    total = 0
    current_user = request.user
    
    #if the cart count is less than or equal to 0, then redirect back to store
    cart_items = CartItem.objects.select_related('product').filter(user=current_user)
    
    if cart_items.count() < 1:
        return redirect('store')

    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        
    tax = (2 * total)/100
    grand_total = total + tax
    
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = current_user
            order.order_total = grand_total
            order.tax = tax
            order.ip = request.META.get('REMOTE_ADDR')

            # Save the order first to get an ID
            order.save()
            
            
            # Genarate order number
            current_date = datetime.now().strftime('%Y%m%d')
            order_number = f'{current_date}{order.id}'
            order.order_number = order_number
            order.save()
            

            return redirect(sslcommerz_payment_gateway(request, order.id, str(current_user.id), grand_total))
        
    else:
        form = OrderForm()
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'orders/place_order.html', context)


def cancel_view(request):
    # Handle canceled payments
    messages.warning(request, 'Your payment was canceled.')
    return render(request, 'orders/payment_cancel.html')

def fail_view(request):
    # Handle failed payments
    messages.error(request, 'Payment failed. Please try again.')
    return render(request, 'orders/payment_fail.html')
 
    
            
            

            
    

            