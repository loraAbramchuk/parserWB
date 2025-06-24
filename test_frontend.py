#!/usr/bin/env python
"""
Тестовый скрипт для проверки работы фронтенда и API
"""
import os
import sys
import django
import requests
import json

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wildberries_parser.settings')
django.setup()

from products.wb_by_parser import parse_wb_by, save_products_to_db

def test_parser():
    """
    Тестируем парсер wildberries.by
    """
    print("🧪 Тестируем парсер wildberries.by...")
    
    try:
        # Парсим небольшое количество товаров для теста
        query = "ноутбук"
        products = parse_wb_by(query, max_pages=1)
        
        if products:
            print(f"✅ Парсер работает! Найдено товаров: {len(products)}")
            
            # Показываем пример товара
            if products:
                product = products[0]
                print(f"📦 Пример товара:")
                print(f"   Название: {product['name'][:50]}...")
                print(f"   Цена: {product['price']} ₽")
                if product['discount_price']:
                    print(f"   Скидка: {product['discount_price']} ₽")
                if product['rating']:
                    print(f"   Рейтинг: {product['rating']}")
                print(f"   Отзывы: {product['reviews_count']}")
            
            # Сохраняем в базу данных
            saved_count = save_products_to_db(products)
            print(f"💾 Сохранено в БД: {saved_count} товаров")
            
        else:
            print("❌ Товары не найдены")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании парсера: {e}")
        import traceback
        traceback.print_exc()

def test_api():
    """
    Тестируем API endpoints
    """
    print("\n🔌 Тестируем API endpoints...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Тест основного API
        response = requests.get(f"{base_url}/api/products/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API работает! Товаров в базе: {len(data.get('results', data))}")
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            
        # Тест статистики
        response = requests.get(f"{base_url}/api/products/stats/")
        if response.status_code == 200:
            stats = response.json()
            print(f"📊 Статистика: {stats}")
        else:
            print(f"❌ Ошибка статистики: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен. Запустите: python manage.py runserver")
    except Exception as e:
        print(f"❌ Ошибка при тестировании API: {e}")

def main():
    """
    Основная функция тестирования
    """
    print("🚀 Тестирование фронтенда и API для Wildberries Parser")
    print("=" * 60)
    
    # Тестируем парсер
    test_parser()
    
    # Тестируем API
    test_api()
    
    print("\n" + "=" * 60)
    print("📋 Инструкции по запуску:")
    print("1. Запустите сервер: python manage.py runserver")
    print("2. Откройте браузер: http://127.0.0.1:8000")
    print("3. Используйте фильтры и сортировку в таблице")
    print("4. Нажмите 'Парсить товары' для добавления новых товаров")
    print("5. Админка: http://127.0.0.1:8000/admin/")
    print("6. API: http://127.0.0.1:8000/api/products/")

if __name__ == "__main__":
    main() 