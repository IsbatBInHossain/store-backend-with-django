from django.shortcuts import render
from django.db.models import F
from store.models import Product, Order, OrderItem


def say_hello(request):
    query_set = Order.objects.select_related('customer').order_by('-placed_at')[:5]
    return render(request, 'hello.html', {'name': 'Isbat', 'products': list(query_set)})
