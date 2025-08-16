# from django.core.management.base import BaseCommand
# from cart.models import Cart, CartItem

# class Command(BaseCommand):
#     help = 'Clean up carts and cart items'

#     def handle(self, *args, **options):
#         carts = Cart.objects.filter(cartitem__isnull=True)
#         count = carts.count()
#         carts.delete()
#         self.stdout.write(f"Deleted {count} orphaned carts")



from django.core.management.base import BaseCommand
from cart.models import Cart, CartItem
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Cleans up orphaned carts and cart items'
    
    def handle(self, *args, **options):
        # Delete carts older than 7 days with no items
        old_carts = Cart.objects.filter(
            cartitem__isnull=True,
            date_added__lt=timezone.now() - timedelta(days=7))
        count = old_carts.count()
        old_carts.delete()
        self.stdout.write(f"Deleted {count} empty carts")
        
        # Delete cart items with no cart or user
        orphan_items = CartItem.objects.filter(cart__isnull=True, user__isnull=True)
        count = orphan_items.count()
        orphan_items.delete()
        self.stdout.write(f"Deleted {count} orphan cart items")