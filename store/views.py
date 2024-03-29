from django.db.models import Count
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .models import Product, Collection, OrderItem, Review
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer


class ProductViewSet(ModelViewSet):
   queryset = Product.objects.all()
   serializer_class = ProductSerializer

   def get_serializer_context(self):
      return {'request': self.request}
   
   def destroy(self, request, *args, **kwargs):  
       if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
          return Response({'Product cannot be deleted because it is associated with one or more order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
       
       return super().destroy(request, *args, **kwargs)
   

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('product'))
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection=kwargs['pk']).count() > 0:
            msg = 'This collection cannot be deleted because it contains one or more products.'
            return Response({'error': msg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    
        

