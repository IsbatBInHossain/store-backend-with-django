from django.shortcuts import render
from store.models import Product


def say_hello(request):
    query_set = Product.objects.all()
    for product in query_set:
        print(product)
    return render(request, 'hello.html', {'name': 'Isbat'})
