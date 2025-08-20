from django.contrib import admin
from .models import Payment, Order, OrderProduct, PaymentGateWaySettings


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'payment_method', 'amount_paid', 'status', 'created_at')
    list_filter = ('payment_method', 'status', 'created_at')
    search_fields = ('payment_id', 'user__email', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'user', 'full_name', 'email', 'phone',
        'order_total', 'tax', 'status', 'is_ordered', 'created_at'
    )
    list_filter = ('status', 'is_ordered', 'created_at', 'country', 'state', 'city')
    search_fields = ('order_number', 'user__email', 'first_name', 'last_name', 'phone')
    readonly_fields = ('order_total', 'tax', 'created_at')
    ordering = ('-created_at',)


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = (
        'order', 'user', 'product', 'quantity', 'product_price',
        'ordered', 'created_at', 'updated_at'
    )
    list_filter = ('ordered', 'created_at', 'updated_at')
    search_fields = ('order__order_number', 'user__email', 'product__product_name')
    ordering = ('-created_at',)

@admin.register(PaymentGateWaySettings)
class PaymentGateWaySettingsAdmin(admin.ModelAdmin):
    list_display = ('store_id', 'store_pass')
    search_fields = ('store_id', 'store_pass')
    ordering = ('store_id',)