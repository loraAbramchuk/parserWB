// Основной класс для управления таблицей товаров
class ProductsTable {
    constructor() {
        this.products = [];
        this.filteredProducts = [];
        this.currentPage = 1;
        this.itemsPerPage = 20;
        this.sortField = null;
        this.sortDirection = 'asc';
        this.filters = {
            minPrice: '',
            maxPrice: '',
            minRating: '',
            minReviews: '',
            search: ''
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadProducts();
        this.updatePriceRange();
    }
    
    // Привязка событий к элементам
    bindEvents() {
        // Фильтры
        document.getElementById('minPrice').addEventListener('input', () => this.applyFilters());
        document.getElementById('maxPrice').addEventListener('input', () => this.applyFilters());
        document.getElementById('minRating').addEventListener('input', () => this.applyFilters());
        document.getElementById('minReviews').addEventListener('input', () => this.applyFilters());
        document.getElementById('searchInput').addEventListener('input', () => this.applyFilters());
        
        // Сортировка
        document.querySelectorAll('th[data-sort]').forEach(th => {
            th.addEventListener('click', () => this.sortBy(th.dataset.sort));
        });
        
        // Кнопки
        document.getElementById('clearFilters').addEventListener('click', () => this.clearFilters());
        document.getElementById('refreshData').addEventListener('click', () => this.loadProducts());
        document.getElementById('parseProducts').addEventListener('click', () => this.parseProducts());
        
        // Пагинация
        document.getElementById('prevPage').addEventListener('click', () => this.prevPage());
        document.getElementById('nextPage').addEventListener('click', () => this.nextPage());
    }
    
    // Загрузка товаров с сервера
    async loadProducts() {
        this.showLoading();
        
        try {
            const response = await fetch('/api/products/');
            if (!response.ok) {
                throw new Error('Ошибка загрузки данных');
            }
            
            const data = await response.json();
            this.products = data.results || data;
            this.applyFilters();
            this.hideLoading();
            this.showNotification('Данные успешно загружены', 'success');
        } catch (error) {
            console.error('Ошибка загрузки товаров:', error);
            this.hideLoading();
            this.showNotification('Ошибка загрузки данных', 'error');
        }
    }
    
    // Применение фильтров
    applyFilters() {
        this.updateFilters();
        
        this.filteredProducts = this.products.filter(product => {
            // Фильтр по цене
            if (this.filters.minPrice && product.price < parseFloat(this.filters.minPrice)) {
                return false;
            }
            if (this.filters.maxPrice && product.price > parseFloat(this.filters.maxPrice)) {
                return false;
            }
            
            // Фильтр по рейтингу
            if (this.filters.minRating && product.rating < parseFloat(this.filters.minRating)) {
                return false;
            }
            
            // Фильтр по количеству отзывов
            if (this.filters.minReviews && product.review_count < parseInt(this.filters.minReviews)) {
                return false;
            }
            
            // Поиск по названию
            if (this.filters.search && !product.name.toLowerCase().includes(this.filters.search.toLowerCase())) {
                return false;
            }
            
            return true;
        });
        
        this.currentPage = 1;
        this.renderTable();
    }
    
    // Обновление фильтров из формы
    updateFilters() {
        this.filters.minPrice = document.getElementById('minPrice').value;
        this.filters.maxPrice = document.getElementById('maxPrice').value;
        this.filters.minRating = document.getElementById('minRating').value;
        this.filters.minReviews = document.getElementById('minReviews').value;
        this.filters.search = document.getElementById('searchInput').value;
    }
    
    // Очистка фильтров
    clearFilters() {
        document.getElementById('minPrice').value = '';
        document.getElementById('maxPrice').value = '';
        document.getElementById('minRating').value = '';
        document.getElementById('minReviews').value = '';
        document.getElementById('searchInput').value = '';
        
        this.filters = {
            minPrice: '',
            maxPrice: '',
            minRating: '',
            minReviews: '',
            search: ''
        };
        
        this.applyFilters();
        this.showNotification('Фильтры очищены', 'info');
    }
    
    // Сортировка
    sortBy(field) {
        if (this.sortField === field) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortField = field;
            this.sortDirection = 'asc';
        }
        
        // Обновление визуальных индикаторов сортировки
        document.querySelectorAll('th[data-sort]').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        
        const currentTh = document.querySelector(`th[data-sort="${field}"]`);
        currentTh.classList.add(`sort-${this.sortDirection}`);
        
        this.renderTable();
    }
    
    // Рендеринг таблицы
    renderTable() {
        const tbody = document.getElementById('productsTableBody');
        const statsElement = document.getElementById('tableStats');
        
        // Сортировка
        let sortedProducts = [...this.filteredProducts];
        if (this.sortField) {
            sortedProducts.sort((a, b) => {
                let aVal = a[this.sortField];
                let bVal = b[this.sortField];
                
                // Обработка null значений
                if (aVal === null || aVal === undefined) aVal = 0;
                if (bVal === null || bVal === undefined) bVal = 0;
                
                // Строковое сравнение для названий
                if (typeof aVal === 'string') {
                    aVal = aVal.toLowerCase();
                    bVal = bVal.toLowerCase();
                }
                
                if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
                if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
                return 0;
            });
        }
        
        // Пагинация
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const paginatedProducts = sortedProducts.slice(startIndex, endIndex);
        
        // Обновление статистики
        statsElement.textContent = `Показано ${paginatedProducts.length} из ${this.filteredProducts.length} товаров`;
        
        // Очистка таблицы
        tbody.innerHTML = '';
        
        // Заполнение таблицы
        paginatedProducts.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <div class="product-name" title="${product.name}">
                        <a href="${product.product_url}" target="_blank">${product.name}</a>
                    </div>
                </td>
                <td>
                    <span class="price">${this.formatPrice(product.price)} ₽</span>
                    ${product.discount_price ? `<br><span class="discount-price">${this.formatPrice(product.discount_price)} ₽</span>` : ''}
                </td>
                <td>
                    ${product.rating ? `
                        <div class="rating">
                            <span class="rating-stars">${this.getStars(product.rating)}</span>
                            <span class="rating-value">${product.rating}</span>
                        </div>
                    ` : 'Нет данных'}
                </td>
                <td>
                    <span class="reviews-count">${product.review_count || 0}</span>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        this.updatePagination();
    }
    
    // Обновление пагинации
    updatePagination() {
        const totalPages = Math.ceil(this.filteredProducts.length / this.itemsPerPage);
        const paginationInfo = document.getElementById('paginationInfo');
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        
        paginationInfo.textContent = `Страница ${this.currentPage} из ${totalPages}`;
        
        prevBtn.disabled = this.currentPage === 1;
        nextBtn.disabled = this.currentPage === totalPages;
    }
    
    // Переход на предыдущую страницу
    prevPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.renderTable();
        }
    }
    
    // Переход на следующую страницу
    nextPage() {
        const totalPages = Math.ceil(this.filteredProducts.length / this.itemsPerPage);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.renderTable();
        }
    }
    
    // Обновление диапазона цен
    updatePriceRange() {
        if (this.products.length > 0) {
            const prices = this.products.map(p => p.price).filter(p => p !== null);
            if (prices.length > 0) {
                const minPrice = Math.min(...prices);
                const maxPrice = Math.max(...prices);
                
                document.getElementById('minPrice').placeholder = `От ${this.formatPrice(minPrice)}`;
                document.getElementById('maxPrice').placeholder = `До ${this.formatPrice(maxPrice)}`;
            }
        }
    }
    
    // Парсинг новых товаров
    async parseProducts() {
        const query = prompt('Введите поисковый запрос для парсинга:');
        if (!query) return;
        
        this.showLoading();
        
        try {
            const response = await fetch('/parse-products/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ query: query })
            });
            
            if (!response.ok) {
                throw new Error('Ошибка парсинга');
            }
            
            const result = await response.json();
            this.showNotification(`Парсинг завершен. Добавлено ${result.saved_count} товаров`, 'success');
            this.loadProducts(); // Перезагружаем данные
        } catch (error) {
            console.error('Ошибка парсинга:', error);
            this.showNotification('Ошибка парсинга товаров', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    // Вспомогательные методы
    formatPrice(price) {
        if (!price) return '0';
        return new Intl.NumberFormat('ru-RU').format(price);
    }
    
    getStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        
        return '★'.repeat(fullStars) + (hasHalfStar ? '☆' : '') + '☆'.repeat(emptyStars);
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    showLoading() {
        const loading = document.getElementById('loading');
        if (loading) loading.style.display = 'block';
    }
    
    hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) loading.style.display = 'none';
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Показываем уведомление
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Скрываем через 3 секунды
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 3000);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new ProductsTable();
}); 