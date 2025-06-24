#!/bin/bash

echo "🧹 Очистка проекта от ненужных файлов..."

# Удаление кэша Python
echo "📦 Удаление Python кэша..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Удаление временных файлов
echo "🗑️ Удаление временных файлов..."
find . -name "*.tmp" -o -name "*.temp" -o -name "*.bak" -o -name "*.backup" -delete 2>/dev/null || true

# Удаление файлов редакторов
echo "📝 Удаление файлов редакторов..."
find . -name "*.swp" -o -name "*.swo" -o -name "*~" -o -name "*#" -o -name ".#*" -delete 2>/dev/null || true

# Удаление системных файлов
echo "💻 Удаление системных файлов..."
find . -name ".DS_Store" -o -name "Thumbs.db" -o -name "ehthumbs.db" -delete 2>/dev/null || true

# Удаление файлов отладки
echo "🐛 Удаление файлов отладки..."
find . -name "debug_page_*.html" -delete 2>/dev/null || true

echo "✅ Очистка завершена!"
echo "📊 Размер проекта: $(du -sh . | cut -f1)" 