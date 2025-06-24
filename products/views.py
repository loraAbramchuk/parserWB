from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View
import json
from .models import Product
from .serializers import ProductSerializer, ProductListSerializer
from .filters import ProductFilter
from django.db import models
from django.core.management import call_command


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для работы с товарами через API
    Поддерживает фильтрацию, поиск и сортировку
    """
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'search_query']
    ordering_fields = ['price', 'original_price', 'rating', 'review_count', 'created_at']
    ordering = ['-created_at']  # По умолчанию сортируем по дате создания (новые сначала)
    
    def get_serializer_class(self):
        """
        Выбираем сериализатор в зависимости от действия
        """
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Получение статистики по товарам
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        stats = {
            'total_products': queryset.count(),
            'avg_price': queryset.aggregate(avg_price=models.Avg('price'))['avg_price'],
            'avg_rating': queryset.aggregate(avg_rating=models.Avg('rating'))['avg_rating'],
            'products_with_discount': queryset.filter(
                original_price__gt=models.F('price')
            ).count(),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Получение списка всех категорий
        """
        categories = Product.objects.values_list('search_query', flat=True).distinct()
        return Response(list(categories))


def products_table_view(request):
    """
    View для отображения таблицы товаров с фильтрами
    """
    return render(request, 'products/products_table.html')


@method_decorator(csrf_exempt, name='dispatch')
class ParseProductsView(View):
    """
    API endpoint для парсинга товаров
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            if not query:
                return JsonResponse({'error': 'Не указан поисковый запрос'}, status=400)
            # Запускаем management-команду парсера через call_command
            call_command('parse_wb_by', query, pages=1)
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
