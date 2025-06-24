from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Product
    """
    list_display = [
        'name', 'price', 'original_price', 'rating', 
        'review_count', 'search_query', 'created_at'
    ]
    list_filter = [
        'search_query', 'rating', 'created_at',
    ]
    search_fields = ['name', 'search_query']
    readonly_fields = ['created_at', 'updated_at', 'has_discount', 'discount_percentage']
    list_per_page = 50
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('wb_id', 'name', 'search_query')
        }),
        ('Цены', {
            'fields': ('price', 'original_price', 'has_discount', 'discount_percentage')
        }),
        ('Рейтинги', {
            'fields': ('rating', 'review_count')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
