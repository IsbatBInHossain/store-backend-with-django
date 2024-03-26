from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http import HttpRequest
from .models import Collection, Product, Promotion, Customer, Cart, CartItem, Order, OrderItem, Address
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse


class InventoryFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'inventory'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "inventory"

    # Constants
    LOW = '<10'
    OK = '>=10'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [
            (self.LOW, 'Low'),
            (self.OK, 'OK'),

        ]

    def queryset(self, request, queryset: QuerySet) -> QuerySet:
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value to decide how to filter the queryset.
        if self.value() == self.LOW:
          return queryset.filter(inventory__lt=10)
        elif self.value() == self.OK:
          return queryset.filter(inventory__gte=10)




@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  actions = ['clear_inventory']
  list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
  list_editable = ['unit_price']
  list_per_page = 15
  list_select_related = ['collection']
  ordering = ['title', 'inventory']
  search_fields = ['title']

  list_filter = ['collection', 'last_update', InventoryFilter]

  @admin.display(ordering='collection__title')
  def collection_title(self, product):
    return product.collection.title

  @admin.display(ordering='inventory')
  def inventory_status(self, product):
    return 'OK' if product.inventory >= 10 else 'Low'
  
  @admin.action(description='Clear inventory of selected products')
  def clear_inventory(self, request: HttpRequest, queryset: QuerySet):
    updated_count = queryset.update(inventory=0)

    self.message_user(
      request,
      f'{updated_count} items has been successfully updated',
      messages.ERROR
    )

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
  list_display = ['first_name', 'last_name', 'membership', 'order_count']
  list_editable = ['membership']
  list_per_page = 15
  ordering = ['first_name', 'last_name']
  search_fields = ['first_name__istartswith', 'last_name__istartswith']

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


class OrderItemInline(admin.TabularInline):
  model = OrderItem
  autocomplete_fields = ['product']
  min_num = 1
  extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  autocomplete_fields = ['customer']
  inlines = [OrderItemInline]
  list_display = ['id','customer', 'placed_at', 'payment_status']
  list_editable = ['payment_status']
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