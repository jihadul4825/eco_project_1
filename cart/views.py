from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem
from .utils import _cart_id
from django.core.exceptions import ObjectDoesNotExist
from category.models import Category
from django.contrib.auth.decorators import login_required



def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        # Use get_or_create to prevent duplicates
        cart_item, created = CartItem.objects.get_or_create(
            product=product,
            user=request.user,
            defaults={'quantity': 0}
        )
        
        # Update quantity
        cart_item.quantity += 1
        cart_item.save()

    else:
        # For anonymous users (existing code)
        cart_id = _cart_id(request)
        cart, created = Cart.objects.get_or_create(cart_id=cart_id)

        cart_item, created = CartItem.objects.get_or_create(
            product=product,
            cart=cart,
            defaults={'quantity': 0}
        )

        # Update quantity
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    
    try:
        product = get_object_or_404(Product, id=product_id)
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
            
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
            
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass
    return redirect('cart')



def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    categories = Category.objects.all()

    try:
        tax=0
        grand_total=0
        
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass # just ignore
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        'categories': categories
    }
    return render(request, 'cart/cart.html', context)

    
    


