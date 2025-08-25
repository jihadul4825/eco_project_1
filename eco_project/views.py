from django.shortcuts import render
from store.models import Product

def home(request):
    products = Product.objects.select_related('category').filter(is_available=True).order_by('-id')
    return render(request, 'home.html', {'products': products})