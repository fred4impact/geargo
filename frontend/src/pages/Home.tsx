import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { itemApi, categoryApi } from '../api/endpoints';
import type { Item, Category } from '../types';
import { getCategoryIcon } from '../utils/categoryIcons';
import './Home.css';

const Home = () => {
  const { data: itemsData, isLoading: itemsLoading, error: itemsError } = useQuery({
    queryKey: ['featured-items'],
    queryFn: async () => {
      try {
        const response = await itemApi.list({ page: 1 });
        const items = response.data.results || [];
        return items;
      } catch (error: unknown) {
        try {
          const recResponse = await itemApi.getRecommendations();
          return Array.isArray(recResponse.data) ? recResponse.data : [];
        } catch {
          return [];
        }
      }
    },
    retry: 2,
    refetchOnWindowFocus: false,
  });

  const items = itemsData || [];

  const { data: categories, isLoading: categoriesLoading, error: categoriesError } = useQuery({
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
    retry: 2,
    refetchOnWindowFocus: false,
  });

  return (
    <div className="home">
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">GearGo</h1>
          <p className="hero-subtitle">
            Rent equipment, book services, and connect with gear owners. Specialist advice, fast service.
          </p>
          <div className="hero-actions">
            <Link to="/items" className="btn btn-primary">
              Browse Items
            </Link>
            <Link to="/login" className="btn btn-secondary">
              Get Started
            </Link>
          </div>
        </div>
      </section>

      <section className="categories">
        <div className="section-container">
          <h2 className="section-title">Categories</h2>
          {categoriesLoading ? (
            <div className="loading">Loading categories...</div>
          ) : categoriesError ? (
            <div className="error-message">
              <p>Unable to load categories. Please check your connection.</p>
            </div>
          ) : categories && categories.length > 0 ? (
            <div className="category-grid">
              {categories.slice(0, 6).map((category: Category) => (
                <Link
                  key={category.id}
                  to={`/items?category=${category.id}`}
                  className="category-card"
                >
                  <span className="category-icon">{getCategoryIcon(category.name, category.icon)}</span>
                  <h3>{category.name}</h3>
                  <p>{category.description || 'Explore items in this category'}</p>
                </Link>
              ))}
            </div>
          ) : (
            <div className="no-items">
              <p>No categories yet. Categories will appear here once they&apos;re added.</p>
            </div>
          )}
        </div>
      </section>

      <section className="featured-items">
        <div className="section-container">
          <div className="featured-header">
            <h2 className="section-title">Featured Items</h2>
            {!itemsLoading && items.length > 0 && (
              <span className="featured-count">{items.length} products</span>
            )}
          </div>
          {itemsLoading ? (
            <div className="loading">Loading items...</div>
          ) : itemsError ? (
            <div className="error-message">
              <p>Unable to load items. <Link to="/items">Browse all items</Link></p>
            </div>
          ) : items.length > 0 ? (
            <div className="items-grid">
              {items.slice(0, 8).map((item: Item) => (
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
                    {item.availability_status && (
                      <span className={`status-badge ${item.availability_status}`}>
                        {item.availability_status}
                      </span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          ) : !itemsLoading && !itemsError ? (
            <div className="no-items">
              <p>No items available yet. Be the first to list an item and start renting!</p>
              <Link to="/items" className="btn btn-primary">Browse All Items</Link>
            </div>
          ) : null}
        </div>
      </section>
    </div>
  );
};

export default Home;
