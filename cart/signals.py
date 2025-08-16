from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .utils import transfer_cart

@receiver(user_logged_in)
def merge_carts(sender, request, user, **kwargs):
    transfer_cart(request, user)


##***** after writing this code *****##
#*-----------------------------------*#

#*** go to app.py and add this code ***#
# def ready(self):
#     import cart.signals

#*** go to settings.py and add this code ***#

# INSTALLED_APPS = [
#     ...
#     'cart.apps.CartConfig',  # Replace 'cart' with this
#     ...
# ]

#*** Run Migrations ***#
# python manage.py makemigrations
# python manage.py migrate

