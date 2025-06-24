import requests
import json
import time
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from .models import Product


class WildberriesParser:
    """
    Парсер для получения данных о товарах с Wildberries
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def search_products(self, query, category=None, limit=100):
        """
        Поиск товаров по запросу
        
        Args:
            query (str): Поисковый запрос
            category (str): Категория товаров (опционально)
            limit (int): Максимальное количество товаров для парсинга
            
        Returns:
            list: Список найденных товаров
        """
        print(f"🔍 Начинаем поиск товаров по запросу: '{query}'")
        
        # Формируем URL для поиска
        search_url = "https://search.wb.ru/exactmatch/ru/common/v4/search"
        
        params = {
            'TestGroup': 'no_test',
            'TestID': 'no_test',
            'appType': '1',
            'curr': 'rub',
            'dest': '-1257786',
            'query': query,
            'resultset': 'catalog',
            'sort': 'popular',
            'spp': '30',
            'suppressSpellcheck': 'false',
        }
        
        if category:
            params['cat'] = category
            print(f"📂 Категория: {category}")
        
        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data or 'products' not in data['data']:
                print("❌ Не удалось получить данные о товарах")
                return []
            
            products = data['data']['products']
            print(f"✅ Найдено товаров: {len(products)}")
            
            # Ограничиваем количество товаров
            if limit and len(products) > limit:
                products = products[:limit]
                print(f"📊 Ограничиваем до {limit} товаров")
            
            return products
            
        except requests.RequestException as e:
            print(f"❌ Ошибка при запросе к API: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка при парсинге JSON: {e}")
            return []
    
    def get_product_details(self, product_id):
        """
        Получение детальной информации о товаре
        
        Args:
            product_id (int): ID товара
            
        Returns:
            dict: Детальная информация о товаре
        """
        detail_url = f"https://card.wb.ru/cards/detail?nm={product_id}"
        
        try:
            response = self.session.get(detail_url)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data or 'products' not in data['data']:
                return None
            
            return data['data']['products'][0]
            
        except (requests.RequestException, json.JSONDecodeError, IndexError):
            return None
    
    def parse_product(self, product_data, search_query, category=None):
        """
        Парсинг данных товара из API ответа
        
        Args:
            product_data (dict): Данные товара из API
            search_query (str): Поисковый запрос
            category (str): Категория товара
            
        Returns:
            dict: Структурированные данные товара
        """
        try:
            # Извлекаем основную информацию
            product_id = product_data.get('id')
            name = product_data.get('name', '')
            
            # Обрабатываем цены
            price_data = product_data.get('salePriceU', 0)
            price = Decimal(str(price_data)) / 100 if price_data else Decimal('0')
            
            original_price_data = product_data.get('priceU', 0)
            original_price = Decimal(str(original_price_data)) / 100 if original_price_data else Decimal('0')
            
            # Определяем основную цену и цену со скидкой
            if original_price > price and price > 0:
                main_price = original_price
                discount_price = price
            else:
                main_price = price
                discount_price = None
            
            # Обрабатываем рейтинг и отзывы
            rating_data = product_data.get('rating', 0)
            rating = Decimal(str(rating_data)) if rating_data else None
            
            reviews_count = product_data.get('reviewCount', 0)
            
            # Формируем URL товара
            product_url = f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx"
            
            # Определяем категорию
            product_category = category or product_data.get('category', 'Неизвестно')
            
            return {
                'name': name,
                'price': main_price,
                'discount_price': discount_price,
                'rating': rating,
                'reviews_count': reviews_count,
                'category': product_category,
                'search_query': search_query,
                'product_url': product_url,
            }
            
        except (KeyError, ValueError, TypeError) as e:
            print(f"❌ Ошибка при парсинге товара {product_data.get('id', 'unknown')}: {e}")
            return None
    
    def save_products(self, products_data):
        """
        Сохранение товаров в базу данных
        
        Args:
            products_data (list): Список данных товаров
            
        Returns:
            int: Количество сохраненных товаров
        """
        saved_count = 0
        
        with transaction.atomic():
            for product_data in products_data:
                if not product_data:
                    continue
                
                try:
                    # Проверяем, существует ли товар с таким URL
                    product, created = Product.objects.get_or_create(
                        product_url=product_data['product_url'],
                        defaults=product_data
                    )
                    
                    if created:
                        saved_count += 1
                        print(f"✅ Сохранен: {product_data['name'][:50]}...")
                    else:
                        # Обновляем существующий товар
                        for field, value in product_data.items():
                            setattr(product, field, value)
                        product.save()
                        print(f"🔄 Обновлен: {product_data['name'][:50]}...")
                        
                except Exception as e:
                    print(f"❌ Ошибка при сохранении товара: {e}")
                    continue
        
        return saved_count
    
    def parse_and_save(self, query, category=None, limit=100):
        """
        Основной метод для парсинга и сохранения товаров
        
        Args:
            query (str): Поисковый запрос
            category (str): Категория товаров
            limit (int): Максимальное количество товаров
            
        Returns:
            int: Количество сохраненных товаров
        """
        print(f"🚀 Начинаем парсинг Wildberries...")
        print(f"📝 Запрос: {query}")
        print(f"📂 Категория: {category or 'Все категории'}")
        print(f"📊 Лимит: {limit} товаров")
        print("-" * 50)
        
        # Получаем список товаров
        products = self.search_products(query, category, limit)
        
        if not products:
            print("❌ Товары не найдены")
            return 0
        
        # Парсим данные каждого товара
        parsed_products = []
        for i, product in enumerate(products, 1):
            print(f"📦 Обрабатываем товар {i}/{len(products)}...")
            
            parsed_product = self.parse_product(product, query, category)
            if parsed_product:
                parsed_products.append(parsed_product)
            
            # Небольшая задержка между запросами
            time.sleep(random.uniform(0.5, 1.5))
        
        print(f"✅ Обработано товаров: {len(parsed_products)}")
        
        # Сохраняем в базу данных
        saved_count = self.save_products(parsed_products)
        
        print("-" * 50)
        print(f"🎉 Парсинг завершен!")
        print(f"📊 Сохранено новых товаров: {saved_count}")
        
        return saved_count


class Command(BaseCommand):
    """
    Django management command для запуска парсера
    """
    help = 'Парсинг товаров с Wildberries'
    
    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='Поисковый запрос')
        parser.add_argument('--category', type=str, help='Категория товаров')
        parser.add_argument('--limit', type=int, default=100, help='Максимальное количество товаров')
    
    def handle(self, *args, **options):
        query = options['query']
        category = options.get('category')
        limit = options.get('limit', 100)
        
        parser = WildberriesParser()
        saved_count = parser.parse_and_save(query, category, limit)
        
        self.stdout.write(
            self.style.SUCCESS(f'Успешно сохранено {saved_count} товаров')
        ) 