# cart/utils.py
from .models import Cart, CartItem

def _cart_id(request):
    if 'preserved_cart_id' in request.session:
        return request.session['preserved_cart_id']
    
    # Create new session if needed
    if not request.session.session_key:
        request.session.create()
    
    return request.session.session_key

def transfer_cart(request, user):
    try:
        # cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.select_related('cart', 'product').filter(cart__cart_id=_cart_id(request), is_active=True)
        
        for item in cart_items:
            # Check for existing items
            existing_items = CartItem.objects.select_related('product').filter(
                user=user, 
                product=item.product,
                is_active=True
            )
            
            if existing_items.exists():
                # Merge quantities
                existing_item = existing_items.first()
                existing_item.quantity += item.quantity
                existing_item.save()
                item.delete()
            else:
                # Transfer item to user
                item.user = user
                item.cart = None
                item.save()
        
        # Delete the anonymous cart
        cart_items.delete()
        return True
    except Cart.DoesNotExist:
        return False