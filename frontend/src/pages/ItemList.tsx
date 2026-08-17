import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useSearchParams } from 'react-router-dom';
import { itemApi, categoryApi } from '../api/endpoints';
import type { Item, Category } from '../types';
import { getCategoryIcon } from '../utils/categoryIcons';
import './ItemList.css';

type SortOption = 'featured' | 'price_asc' | 'price_desc' | 'newest';

const ItemList = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(
    searchParams.get('category') ? parseInt(searchParams.get('category')!, 10) : null
  );
  const [sort, setSort] = useState<SortOption>('featured');

  const { data: itemsData, isLoading } = useQuery({
    queryKey: ['items', search, selectedCategory, sort],
    queryFn: async () => {
      const params: Record<string, string | number> = { page: 1 };
      if (search) params.search = search;
      if (selectedCategory) params.category = selectedCategory;
      if (sort === 'price_asc') params.ordering = 'daily_price';
      if (sort === 'price_desc') params.ordering = '-daily_price';
      if (sort === 'newest') params.ordering = '-created_at';
      const response = await itemApi.list(params);
      return response.data;
    },
  });

  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      try {
        const response = await categoryApi.list();
        const data = response.data as { results?: Category[] } | Category[];
        if (Array.isArray(data)) return data;
        if (data?.results) return data.results;
        return [];
      } catch {
        return [];
      }
    },
  });

  const categories = Array.isArray(categoriesData) ? categoriesData : [];
  const results = itemsData?.results ?? [];
  const count = itemsData?.count ?? results.length;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (selectedCategory) params.set('category', selectedCategory.toString());
    setSearchParams(params);
  };

  return (
    <div className="item-list-page">
      <div className="page-header">
        <div className="page-header-inner">
          <h1>Browse Items</h1>
          <form onSubmit={handleSearch} className="search-form">
            <input
              type="text"
              placeholder="Search items..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="search-input"
            />
            <button type="submit" className="btn btn-primary">
              Search
            </button>
          </form>
        </div>
      </div>

      <div className="item-list-container">
        <aside className="filters">
          <h3>Filter</h3>
          <div className="category-filters">
            <button
              type="button"
              className={`filter-btn ${!selectedCategory ? 'active' : ''}`}
              onClick={() => setSelectedCategory(null)}
            >
              All
            </button>
            {categories.length > 0 ? (
              categories.map((category: Category) => (
                <button
                  key={category.id}
                  type="button"
                  className={`filter-btn ${selectedCategory === category.id ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(category.id)}
                >
                  <span>{getCategoryIcon(category.name, category.icon)}</span>
                  {category.name}
                </button>
              ))
            ) : (
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>No categories</p>
            )}
          </div>
        </aside>

        <main>
          <div className="list-toolbar">
            <span className="list-count">
              {isLoading ? '...' : `${count} product${count !== 1 ? 's' : ''}`}
            </span>
            <div className="list-sort">
              <label htmlFor="sort">Sort by</label>
              <select
                id="sort"
                value={sort}
                onChange={(e) => setSort(e.target.value as SortOption)}
              >
                <option value="featured">Featured</option>
                <option value="newest">Date, new to old</option>
                <option value="price_asc">Price, low to high</option>
                <option value="price_desc">Price, high to low</option>
              </select>
            </div>
          </div>

          <div className="items-grid">
            {isLoading ? (
              <div className="loading">Loading items...</div>
            ) : results.length > 0 ? (
              results.map((item: Item) => (
                <Link key={item.id} to={`/items/${item.id}`} className="item-card">
                  {item.images?.length > 0 ? (
                    <img
                      src={item.images[0].thumbnail_url || item.images[0].image_url}
                      alt={item.title}
                      className="item-image"
                    />
                  ) : (
                    <div className="item-image-placeholder">No Image</div>
                  )}
                  <div className="item-info">
                    <h3>{item.title}</h3>
                    <p className="item-price">${item.daily_price}/day</p>
                    <p className="item-location">{item.location}</p>
                    <span className={`status-badge ${item.availability_status}`}>
                      {item.availability_status}
                    </span>
                  </div>
                </Link>
              ))
            ) : (
              <div className="no-items">
                <p>No items found.</p>
                {search && <p className="no-items-hint">Try adjusting your search or filters.</p>}
                {!search && (
                  <Link to="/" className="btn btn-primary">Go to Home</Link>
                )}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default ItemList;
