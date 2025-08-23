from django.shortcuts import render, redirect, get_object_or_404
from .models import Product 
from category.models import Category
from cart.models import CartItem

from cart.views import _cart_id

# from .forms import ReviewForm
from orders.models import OrderProduct

from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator



def store(request, category_slug=None):
    # categories = None
    products = None

    if category_slug != None:
        # category = get_object_or_404(Category, slug=category_slug)
        # products = Product.objects.filter(category=category, is_available=True)
        products = Product.objects.select_related('category').filter(category__slug=category_slug, is_available=True)
        
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        
        product_count = products.count()
    else:
        # products = Product.objects.all().filter(is_available=True).order_by('id')
        products = Product.objects.select_related().filter(is_available=True).order_by('id')
        
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        
        product_count = products.count()

    context = {
        'products': paged_products,
        'p_count': product_count,
    }
    return render(request, 'store/store.html',context)


def product_detail(request, category_slug, product_slug):
    try:
        # single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        single_product = Product.objects.select_related('category').get(category__slug=category_slug, slug=product_slug)
        # in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        in_cart = CartItem.objects.prefetch_related('product', 'cart').filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product_details.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.select_related('category').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword),
                is_available=True
            ).order_by('id')
            product_count = products.count()

            # Pagination
            paginator = Paginator(products, 3)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            
            print(request.GET)

            context = {
                'products': paged_products,
                'product_count': product_count,
            }
            return render(request, 'store/store.html', context)
        else:
            # If keyword is empty, redirect to store
            return redirect('store')
    else:
        return redirect('store')