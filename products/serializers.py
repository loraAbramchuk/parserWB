from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product
    """
    has_discount = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    discount_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'wb_id', 'name', 'price', 'original_price', 'discount_price',
            'rating', 'review_count', 'search_query', 'created_at', 
            'updated_at', 'has_discount', 'discount_percentage'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для списка товаров
    """
    has_discount = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    discount_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'wb_id', 'name', 'price', 'original_price', 'discount_price',
            'rating', 'review_count', 'has_discount', 'discount_percentage'
        ] 