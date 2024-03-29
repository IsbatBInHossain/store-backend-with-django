from rest_framework import serializers
from .models import Product, Collection, Review, Cart, CartItem
from decimal import Decimal


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)

class ProductSerializer (serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection']

  price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

  def calculate_tax(self, product: Product):
    return (product.unit_price * Decimal(1.1)).quantize(Decimal('0.01'))
  

class ReviewSerializer (serializers.ModelSerializer):
   class Meta:
      model = Review
      fields = ['id', 'date', 'name', 'description']

   def create(self, validated_data):
      product_id = self.context['product_id']
      return Review.objects.create(product_id=product_id, **validated_data)
   

class SimpleProductSerializer (serializers.ModelSerializer):
   class Meta:
      model = Product
      fields = ['id', 'title', 'unit_price']


class CartItemSerializer (serializers.ModelSerializer):
   class Meta:
      model = CartItem
      fields = ['id', 'product', 'quantity', 'total_price']
      read_only_fields = ['id']

   product = SimpleProductSerializer()
   total_price = serializers.SerializerMethodField(method_name='get_total_price', read_only=True)

   def get_total_price(self, cart_item: CartItem):
      return cart_item.product.unit_price * cart_item.quantity

class AddCartItemSerializer(serializers.ModelSerializer):
   product_id = serializers.IntegerField()

   def validate_product_id(self, value):
      if not Product.objects.filter(pk=value).exists():
         raise serializers.ValidationError("No product found with the given id")
      else:
         return value

   def save(self, **kwargs):
      cart_id = self.context['cart_id']
      product_id = self.validated_data['product_id']
      quantity = self.validated_data['quantity']

      try:
        cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
        cart_item.quantity += quantity
        cart_item.save()
        self.instance = cart_item
      except CartItem.DoesNotExist:
        self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
      
      return self.instance

   class Meta:
      model = CartItem
      fields = ['id', 'product_id', 'quantity']

class UpdateCartItemSerializer(serializers.ModelSerializer):
   class Meta:
      model = CartItem
      fields = ['quantity']

class CartSerializer (serializers.ModelSerializer):
   class Meta:
      model = Cart
      fields = ['id', 'items', 'total_price']

   id = serializers.UUIDField(read_only=True)
   items = CartItemSerializer(many=True, read_only=True)
   total_price = serializers.SerializerMethodField(method_name='get_total_price')

   def get_total_price(self, cart: Cart):
      return sum([item.product.unit_price * item.quantity for item in cart.items.all()])
      
