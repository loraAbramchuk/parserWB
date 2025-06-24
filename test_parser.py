#!/usr/bin/env python
"""
Тестовый скрипт для проверки работы парсера Wildberries
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wildberries_parser.settings')
django.setup()

from products.parser import WildberriesParser

def test_parser():
    """
    Тестируем парсер на небольшом количестве товаров
    """
    print("🧪 Тестируем парсер Wildberries...")
    
    parser = WildberriesParser()
    
    # Тестируем поиск товаров
    query = "ноутбук"
    limit = 5  # Ограничиваем до 5 товаров для теста
    
    print(f"🔍 Поиск товаров по запросу: '{query}'")
    print(f"📊 Лимит: {limit} товаров")
    print("-" * 50)
    
    try:
        # Получаем список товаров
        products = parser.search_products(query, limit=limit)
        
        if not products:
            print("❌ Товары не найдены")
            return
        
        print(f"✅ Найдено товаров: {len(products)}")
        
        # Парсим данные каждого товара
        parsed_products = []
        for i, product in enumerate(products, 1):
            print(f"📦 Обрабатываем товар {i}/{len(products)}...")
            
            parsed_product = parser.parse_product(product, query)
            if parsed_product:
                parsed_products.append(parsed_product)
                print(f"  ✅ {parsed_product['name'][:50]}...")
                print(f"     💰 Цена: {parsed_product['price']}₽")
                if parsed_product['discount_price']:
                    print(f"     🎯 Скидка: {parsed_product['discount_price']}₽")
                if parsed_product['rating']:
                    print(f"     ⭐ Рейтинг: {parsed_product['rating']}")
                print(f"     💬 Отзывы: {parsed_product['reviews_count']}")
                print()
        
        print(f"✅ Обработано товаров: {len(parsed_products)}")
        
        # Сохраняем в базу данных
        if parsed_products:
            saved_count = parser.save_products(parsed_products)
            print(f"💾 Сохранено в БД: {saved_count} товаров")
        
        print("🎉 Тест завершен успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parser() 