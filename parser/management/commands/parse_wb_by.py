import json
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Product
import requests
from urllib.parse import quote


class Command(BaseCommand):
    help = 'Парсинг товаров с wildberries.by через API'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='Поисковый запрос')
        parser.add_argument('--pages', type=int, default=1, help='Количество страниц для парсинга')
        parser.add_argument('--category', type=str, help='Категория товаров')

    def handle(self, *args, **options):
        query = options['query']
        pages = options['pages']
        category = options['category']

        self.stdout.write(f"Парсим wildberries.by: '{query}', страниц: {pages}, категория: {category}")
        
        total_products = 0
        saved_products = 0

        for page in range(1, pages + 1):
            self.stdout.write(f"📄 Обрабатываем страницу {page}...")
            
            try:
                # Используем API wildberries для поиска товаров
                products = self.get_products_from_api(query, page)
                
                if products:
                    self.stdout.write(f"✅ Найдено {len(products)} товаров на странице {page}")
                    
                    # Сохраняем товары в базу данных
                    page_saved = self.save_products(products, query)
                    saved_products += page_saved
                    total_products += len(products)
                    
                    self.stdout.write(f"💾 Сохранено {page_saved} товаров с страницы {page}")
                else:
                    self.stdout.write(f"❌ Товары не найдены на странице {page}")
                
                # Пауза между запросами
                time.sleep(1)
                
            except Exception as e:
                self.stdout.write(f"❌ Ошибка при обработке страницы {page}: {str(e)}")
                continue

        self.stdout.write(f"🎉 Парсинг завершен! Найдено товаров: {total_products}")
        self.stdout.write(f"Сохранено товаров: {saved_products}")

    def get_products_from_api(self, query, page):
        """Получаем товары через API wildberries"""
        try:
            # URL для API поиска wildberries
            search_url = "https://search.wb.ru/exactmatch/ru/common/v4/search"
            
            # Параметры запроса
            params = {
                'query': query,
                'appType': '1',
                'curr': 'byn',
                'dest': '-59208',
                'lang': 'ru',
                'page': page,
                'reg': '0',
                'regions': '80,83,4,64,38,40,33,70,82,69,86,30,85,22,66,31,48,1,68',
                'resultset': 'catalog',
                'sort': 'popular',
                'spp': '0',
                'suppressSpellcheck': 'false',
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.wildberries.by/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
            }
            
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Добавляем подробный вывод для диагностики
            self.stdout.write(f"🔍 Ответ API: {data}")
            
            if 'data' in data and 'products' in data['data']:
                return data['data']['products']
            else:
                self.stdout.write(f"⚠️ Неожиданная структура ответа API: {data.keys()}")
                if 'error' in data:
                    self.stdout.write(f"❌ Ошибка API: {data['error']}")
                if 'code' in data:
                    self.stdout.write(f"❌ Код ошибки: {data['code']}")
                return []
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(f"❌ Ошибка запроса к API: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            self.stdout.write(f"❌ Ошибка парсинга JSON: {str(e)}")
            return []
        except Exception as e:
            self.stdout.write(f"❌ Неожиданная ошибка: {str(e)}")
            return []

    def save_products(self, products, search_query):
        """Сохраняем товары в базу данных"""
        saved_count = 0
        
        with transaction.atomic():
            for product_data in products:
                try:
                    # Извлекаем данные о товаре
                    name = product_data.get('name', '')
                    price = product_data.get('salePriceU', 0) / 100  # Цена в копейках
                    original_price = product_data.get('priceU', 0) / 100
                    
                    # Получаем рейтинг и количество отзывов
                    rating = product_data.get('rating', 0)
                    review_count = (
                        product_data.get('reviewCount') or
                        product_data.get('feedbacks') or
                        product_data.get('nmFeedbacks') or
                        0
                    )
                    
                    # Получаем ID товара
                    product_id = product_data.get('id', 0)
                    
                    # Проверяем, существует ли товар с таким ID
                    if Product.objects.filter(wb_id=product_id).exists():
                        continue
                    
                    # Создаем новый товар
                    product = Product.objects.create(
                        wb_id=product_id,
                        name=name,
                        price=price,
                        original_price=original_price,
                        rating=rating,
                        review_count=review_count,
                        search_query=search_query
                    )
                    
                    saved_count += 1
                    
                except Exception as e:
                    self.stdout.write(f"❌ Ошибка сохранения товара: {str(e)}")
                    continue
        
        return saved_count 