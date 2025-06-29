# Generated by Django 4.2.23 on 2025-06-24 14:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Полное название товара', max_length=500, verbose_name='Название товара')),
                ('price', models.DecimalField(decimal_places=2, help_text='Оригинальная цена товара', max_digits=10, verbose_name='Цена')),
                ('discount_price', models.DecimalField(blank=True, decimal_places=2, help_text='Цена товара со скидкой (если есть)', max_digits=10, null=True, verbose_name='Цена со скидкой')),
                ('rating', models.DecimalField(blank=True, decimal_places=2, help_text='Рейтинг товара от 0 до 5', max_digits=3, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Рейтинг')),
                ('reviews_count', models.IntegerField(default=0, help_text='Количество отзывов на товар', verbose_name='Количество отзывов')),
                ('category', models.CharField(help_text='Категория товара', max_length=200, verbose_name='Категория')),
                ('search_query', models.CharField(help_text='Запрос, по которому был найден товар', max_length=200, verbose_name='Поисковый запрос')),
                ('product_url', models.URLField(help_text='Ссылка на страницу товара на Wildberries', max_length=500, verbose_name='Ссылка на товар')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления записи')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товары',
                'ordering': ['-created_at'],
                'unique_together': {('product_url',)},
            },
        ),
    ]
