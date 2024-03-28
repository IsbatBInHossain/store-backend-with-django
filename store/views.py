from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Collection
from .serializers import ProductSerializer, CollectionSerializer

# Create your views here.

@api_view(['GET', 'POST'])
def product_list(request: Request):
  if request.method == 'GET':
    queryset = Product.objects.select_related('collection').all()
    serializer = ProductSerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data)
  elif request.method == 'POST':
     serializer = ProductSerializer(data=request.data)
     serializer.is_valid(raise_exception=True)
     serializer.save()
     return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request: Request, id):
    product = get_object_or_404(Product, pk=id)
    if request.method == 'GET':
      serializer = ProductSerializer(product)
      return Response(serializer.data)
    elif request.method == 'PUT':
       serializer = ProductSerializer(product, data=request.data)
       serializer.is_valid(raise_exception=True)
       serializer.save()
       return Response(serializer.data)
    elif request.method == 'DELETE':
       if product.orderitem_set.count() > 0:
          return Response({'Product cannot be deleted because it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
       else:
          product.delete()
          return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST'])
def collection_list(request: Request):
  if request.method == 'GET':
    queryset = Collection.objects.annotate(product_count=Count('product')).all()
    serializer = CollectionSerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data)
  elif request.method == 'POST':
     serializer = CollectionSerializer(data=request.data)
     serializer.is_valid(raise_exception=True)
     serializer.save()
     return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view()
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    serializer = CollectionSerializer(collection)
    return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request: Request, id):
    collection = get_object_or_404(Collection, pk=id)
    if request.method == 'GET':
      serializer = CollectionSerializer(collection)
      return Response(serializer.data)
    elif request.method == 'PUT':
       serializer = CollectionSerializer(collection, data=request.data)
       serializer.is_valid(raise_exception=True)
       serializer.save()
       return Response(serializer.data)
    elif request.method == 'DELETE':
       if collection.product_set.count() > 0:
          return Response({'Collection cannot be deleted because it is associated with a product'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
       else:
          collection.delete()
          return Response(status=status.HTTP_204_NO_CONTENT)

