"""
⚠️ АВТОРСКИЕ ПРАВА И ЛИЦЕНЗИЯ ⚠️

Copyright (c) 2024 [Ваше имя]. Все права защищены.

ПРЕДУПРЕЖДЕНИЕ: ЧАСТНАЯ СОБСТВЕННОСТЬ

Данный файл содержит модели данных и является частной собственностью.
Любое копирование, распространение или коммерческое использование строго запрещено
без письменного разрешения автора.

ЗАПРЕЩЕНО:
- Копирование кода
- Использование в коммерческих целях
- Распространение третьим лицам
- Модификация без разрешения

Для получения разрешений: [ваш-email@example.com]

"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Product(models.Model):
    """
    Модель для хранения данных о товарах с Wildberries
    """
    wb_id = models.BigIntegerField(
        verbose_name="ID товара на Wildberries",
        unique=True,
        default=0,
        help_text="Уникальный идентификатор товара на Wildberries"
    )
    name = models.CharField(
        max_length=500, 
        verbose_name="Название товара",
        help_text="Полное название товара"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Цена со скидкой",
        help_text="Текущая цена товара (со скидкой)"
    )
    original_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Оригинальная цена",
        default=0,
        help_text="Оригинальная цена товара без скидки"
    )
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        verbose_name="Рейтинг",
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        null=True, 
        blank=True,
        help_text="Рейтинг товара от 0 до 5"
    )
    review_count = models.IntegerField(
        verbose_name="Количество отзывов",
        default=0,
        help_text="Количество отзывов на товар"
    )
    search_query = models.CharField(
        max_length=200, 
        verbose_name="Поисковый запрос",
        help_text="Запрос, по которому был найден товар"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата создания записи"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Дата обновления записи"
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name[:50]} - {self.price}₽"

    @property
    def has_discount(self):
        """Проверяет, есть ли скидка на товар"""
        return self.original_price > self.price

    @property
    def discount_percentage(self):
        """Вычисляет процент скидки"""
        if self.has_discount:
            return round(((self.original_price - self.price) / self.original_price) * 100, 1)
        return 0

    @property
    def discount_price(self):
        """Возвращает цену со скидкой (для совместимости)"""
        return self.price
