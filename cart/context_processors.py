from .models import Cart, CartItem
from .views import _cart_id


def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)


##* after write this code go to settings.py **## 
##* and add this code in TEMPLATES

##* TEMPLATES = [
##*     {
##*         'BACKEND': '........................',
##*         'DIRS': [.................],
##*         'APP_DIRS': ........,
##*         'OPTIONS': {
##*             'context_processors': [
##*                 '..........................',
##*                 '..........................',
##*                 '..........................',
##*                 '..........................',
##*                 'category.context_processors.counter',  # <-- add this
##*             ],
##*         },
##*     },
##* ]
            