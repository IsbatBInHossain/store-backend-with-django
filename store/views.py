from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, Collection
from .serializers import ProductSerializer, CollectionSerializer

# Create your views here.

class ProductList(APIView):
   def get(self, request):
      queryset = Product.objects.select_related('collection').all()
      serializer = ProductSerializer(queryset, many=True, context={'request': request})
      return Response(serializer.data)
   
   
   def post(self, request):
      serializer = ProductSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetails(APIView):
   def __get_product(self, id):
      return get_object_or_404(Product, pk=id)

   def get(self, request, id):
      product = self.__get_product(id)
      if request.method == 'GET':
         serializer = ProductSerializer(product)
         return Response(serializer.data)
      

   def put(self, request, id):
      product = self.__get_product(id)
      serializer = ProductSerializer(product, data=request.data)
      serializer.is_valid(raise_exception=True)
      serializer.save()
      return Response(serializer.data)
   
   def delete(self, request, id):
      product = self.__get_product(id)
      if product.orderitem_set.count() > 0:
          return Response({'Product cannot be deleted because it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
      else:
         product.delete()
         return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET','POST'])
def collection_list(request):
    if request.method == 'GET':
        queryset = Collection.objects.all()
        serializer = CollectionSerializer(queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return  Response(serializer.data,status=status.HTTP_201_CREATED)

@api_view(['GET','PUT','DELETE'])
def collection_details(request,pk):
    collection = get_object_or_404(Collection, pk=pk)
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        if collection.product_set.count() > 0:
            msg = 'This collection cannot be deleted because it contains one or more products.'
            return Response({'error': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

