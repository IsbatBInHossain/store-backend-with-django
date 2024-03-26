from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from .models import Collection, Product, Promotion, Customer, Cart, CartItem, Order, OrderItem, Address
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
  list_editable = ['unit_price']
  list_per_page = 15
  list_select_related = ['collection']

  @admin.display(ordering='collection__title')
  def collection_title(self, product):
    return product.collection.title

  @admin.display(ordering='inventory')
  def inventory_status(self, product):
    return 'OK' if product.inventory >= 10 else 'Low'

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
  list_display = ['first_name', 'last_name', 'membership', 'order_count']
  list_editable = ['membership']
  ordering = ['first_name', 'last_name']
  list_per_page = 15

  @admin.display(ordering='order_count')
  def order_count(self, customer):
    url = (reverse('admin:store_order_changelist') 
           + '?'
           + urlencode({
             'customer__id': str(customer.id)
           })
           )
    return format_html('<a href="{}">{}</a>', url, customer.order_count)

  def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
    return super().get_queryset(request).annotate(order_count=Count('order'))

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  list_display = ['id','customer', 'placed_at', 'payment_status']
  list_editable = ['payment_status']
  ordering = ['id']
  list_per_page = 15
  list_select_related = ['customer']

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
  list_display = ['title', 'product_count']
  list_per_page = 15

  @admin.display(ordering='product_count')
  def product_count(self, collection):
    url = (reverse('admin:store_product_changelist') 
           + '?'
           + urlencode({
             'collection__id': str(collection.id)
           })
           )
    return format_html('<a href="{}">{}</a>', url, collection.product_count)
  
  def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
    return super().get_queryset(request).annotate(product_count = Count('product'))

admin.site.register(Promotion)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(Address)