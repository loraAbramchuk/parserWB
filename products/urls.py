from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, products_table_view, ParseProductsView

# Создаем роутер для ViewSet
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    # Подключаем все маршруты роутера
    path('api/', include(router.urls)),
    
    # Главная страница с таблицей товаров
    path('', products_table_view, name='products_table'),
    
    # API для парсинга товаров
    path('parse-products/', ParseProductsView.as_view(), name='parse_products'),
] 