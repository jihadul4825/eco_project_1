from django.shortcuts import render, redirect
from .models import Product 
from category.models import Category
from cart.models import CartItem
from .forms import ReviewForm
from .review_utils import ReviewStatus, submit_review

from cart.views import _cart_id

# from .forms import ReviewForm
# from orders.models import OrderProduct

from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator



# def store(request, category_slug=None):
#     products = None
#     if category_slug != None:
#         # category = get_object_or_404(Category, slug=category_slug)
#         # products = Product.objects.filter(category=category, is_available=True)
#         products = Product.objects.select_related('category').filter(category__slug=category_slug, is_available=True)
        
#         paginator = Paginator(products, 2)
#         page = request.GET.get('page')
#         paged_products = paginator.get_page(page)
        
#         product_count = products.count()
#     else:
#         # products = Product.objects.all().filter(is_available=True).order_by('id')
#         # avoid N+1 problem for products
#         products = Product.objects.select_related('category').filter(is_available=True).order_by('id')
#         paginator = Paginator(products, 3)
#         page = request.GET.get('page')
#         paged_products = paginator.get_page(page)
        
#         product_count = products.count()

#     context = {
#         'products': paged_products,
#         'p_count': product_count,
#     }
#     return render(request, 'store/store.html',context)


def store(request, category_slug=None):
    # Get all available products initially
    products = Product.objects.select_related('category').filter(is_available=True)
    
    # Category filter
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Search functionality
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = products.filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
    
    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        products = products.filter(price__gte=int(min_price))
    if max_price:
        products = products.filter(price__lte=int(max_price))
    
    # Order and count
    products = products.order_by('-id')
    product_count = products.count()

    # Pagination
    paginator = Paginator(products, 3 if not category_slug else 2)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'p_count': product_count,
    }
    
    
    # Add price filters to context if the exist
    if min_price:
        context['min_price'] = min_price
    if max_price:
        context['max_price'] = max_price
    
    return render(request, 'store/store.html', context)
    
    


# def product_detail(request, category_slug, product_slug):
#     try:
#         # single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
#         single_product = Product.objects.select_related('category').get(category__slug=category_slug, slug=product_slug)
#         # in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
#         in_cart = CartItem.objects.prefetch_related('product', 'cart').filter(cart__cart_id=_cart_id(request), product=single_product).exists()
#     except Exception as e:
#         raise e
    
#     context = {
#         'single_product': single_product,
#         'in_cart': in_cart,
#     }
#     return render(request, 'store/product_details.html', context)

def product_detail(request, category_slug, product_slug):
    product = Product.objects.select_related('category').get(category__slug = category_slug, slug = product_slug)
    
    
    in_cart = CartItem.objects.select_related('cart').filter(cart__cart_id=_cart_id(request), product=product).exists()
    
    # Get reviews with users (solves N+1)
    reviews = product.get_reviews_with_users()
    
    # Check if user can review
    review_status = ReviewStatus(request.user, product)
    
    
    # Handle form submission
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        success, message = submit_review(request, product, form)

        if success:
           # Refresh the page to show the new review
           return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)
        else:
            messages.error(request, message)
    
    else:
        form = ReviewForm()

    context = {
        'single_product': product,
        'reviews': reviews,
        'form': form,
        'in_cart': in_cart,
        'can_review': review_status.can_review,
        'has_ordered': review_status.has_ordered,
        'has_reviewed': review_status.has_reviewed,
        'average_rating': product.get_average_rating(),
        'review_count': product.get_review_count(),
    }
    return render(request, 'store/product_details.html', context)
    



