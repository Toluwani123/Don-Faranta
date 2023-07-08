from rest_framework import serializers
from .models import *
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Orders
        fields = ['order_key', 'session_id','item_names', 'get_total_amount']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"

class TrackOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tracking
        fields = "__all__"