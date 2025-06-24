import django_filters
from django.db import models
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Фильтр для товаров с поддержкой фильтрации по цене, рейтингу и количеству отзывов
    """
    # Фильтрация по цене со скидкой
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Фильтрация по оригинальной цене
    min_original_price = django_filters.NumberFilter(field_name='original_price', lookup_expr='gte')
    max_original_price = django_filters.NumberFilter(field_name='original_price', lookup_expr='lte')
    
    # Фильтрация по рейтингу
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    
    # Фильтрация по количеству отзывов
    min_reviews = django_filters.NumberFilter(field_name='review_count', lookup_expr='gte')
    max_reviews = django_filters.NumberFilter(field_name='review_count', lookup_expr='lte')
    
    # Фильтрация по поисковому запросу
    search_query = django_filters.CharFilter(field_name='search_query', lookup_expr='icontains')
    
    # Фильтрация по названию товара
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    # Фильтрация товаров со скидкой
    has_discount = django_filters.BooleanFilter(method='filter_has_discount')
    
    class Meta:
        model = Product
        fields = {
            'price': ['exact', 'gte', 'lte'],
            'original_price': ['exact', 'gte', 'lte'],
            'rating': ['exact', 'gte', 'lte'],
            'review_count': ['exact', 'gte', 'lte'],
            'search_query': ['exact', 'icontains'],
            'name': ['exact', 'icontains'],
        }
    
    def filter_has_discount(self, queryset, name, value):
        """
        Фильтрует товары со скидкой
        """
        if value:
            return queryset.filter(original_price__gt=models.F('price'))
        return queryset 