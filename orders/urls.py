from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('success/', views.success_view, name='success'),
    path('cancel/', views.cancel_view, name='cancel'),  
    path('fail/', views.fail_view, name='fail'),      
]
