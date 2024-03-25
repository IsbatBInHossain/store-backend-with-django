from django.shortcuts import render
from store.models import Product


def say_hello(request):
    query_set = Product.objects.filter(unit_price__gte=50)
    return render(request, 'hello.html', {'name': 'Isbat', 'products': list(query_set)})
