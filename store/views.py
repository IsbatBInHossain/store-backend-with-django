from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Product, Collection, OrderItem, Review, Cart, CartItem
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer
from .filters import ProductFilter
from .paginations import DefaultPagination


class ProductViewSet(ModelViewSet):
   queryset = Product.objects.all()
   serializer_class = ProductSerializer
   filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
   filterset_class = ProductFilter
   search_fields = ['title', 'description']
   ordering_fields = ['unit_price', 'last_update']
   pagination_class = DefaultPagination

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
    

class CartViewSet(CreateModelMixin, 
                  RetrieveModelMixin, 
                  DestroyModelMixin, 
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        else:
            return CartItemSerializer
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id = self.kwargs['cart_pk']).select_related('product')
    
        

