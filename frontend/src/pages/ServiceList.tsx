import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useSearchParams } from 'react-router-dom';
import { serviceApi, serviceCategoryApi } from '../api/endpoints';
import type { Service, ServiceCategory } from '../types';
import './ServiceList.css';

type SortOption = 'featured' | 'rate_asc' | 'rate_desc' | 'newest';

const ServiceList = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(
    searchParams.get('category') ? parseInt(searchParams.get('category')!, 10) : null
  );
  const [sort, setSort] = useState<SortOption>('featured');

  const { data: servicesData, isLoading } = useQuery({
    queryKey: ['services', search, selectedCategory, sort],
    queryFn: async () => {
      const params: Record<string, string | number | boolean> = { available: true };
      if (search) params.search = search;
      if (selectedCategory) params.category = selectedCategory;
      if (sort === 'rate_asc') params.ordering = 'hourly_rate';
      if (sort === 'rate_desc') params.ordering = '-hourly_rate';
      if (sort === 'newest') params.ordering = '-created_at';
      const response = await serviceApi.list(params);
      return response.data;
    },
  });

  const { data: categoriesData } = useQuery({
    queryKey: ['service-categories'],
    queryFn: async () => {
      try {
        const response = await serviceCategoryApi.list();
        const data = response.data as { results?: ServiceCategory[] } | ServiceCategory[];
        if (Array.isArray(data)) return data;
        if (data?.results) return data.results;
        return [];
      } catch {
        return [];
      }
    },
  });

  const categories = Array.isArray(categoriesData) ? categoriesData : [];
  const results = servicesData?.results ?? [];
  const count = servicesData?.count ?? results.length;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (selectedCategory) params.set('category', selectedCategory.toString());
    setSearchParams(params);
  };

  return (
    <div className="service-list-page">
      <div className="page-header">
        <div className="page-header-inner">
          <h1>Browse Services</h1>
          <form onSubmit={handleSearch} className="search-form">
            <input
              type="text"
              placeholder="Search services..."
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

      <div className="service-list-container">
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
              categories.map((category: ServiceCategory) => (
                <button
                  key={category.id}
                  type="button"
                  className={`filter-btn ${selectedCategory === category.id ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(category.id)}
                >
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
              {isLoading ? '...' : `${count} service${count !== 1 ? 's' : ''}`}
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
                <option value="rate_asc">Rate, low to high</option>
                <option value="rate_desc">Rate, high to low</option>
              </select>
            </div>
          </div>

          <div className="services-grid">
            {isLoading ? (
              <div className="loading">Loading services...</div>
            ) : results.length > 0 ? (
              results.map((service: Service) => (
                <Link key={service.id} to={`/services/${service.id}`} className="service-card">
                  <span className="service-card-category">{service.category?.name}</span>
                  <h3>{service.title}</h3>
                  <p className="service-rate">${service.hourly_rate}/hr</p>
                  <p className="service-location">{service.location}</p>
                  <p className="service-provider">by {service.provider?.full_name || 'GearGo Provider'}</p>
                  {service.average_rating > 0 && (
                    <p className="service-rating">
                      ★ {service.average_rating.toFixed(1)} ({service.total_reviews})
                    </p>
                  )}
                </Link>
              ))
            ) : (
              <div className="no-items">
                <p>No services found.</p>
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

export default ServiceList;
