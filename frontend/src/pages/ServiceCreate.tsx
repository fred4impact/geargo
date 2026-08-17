import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { serviceApi, serviceCategoryApi } from '../api/endpoints';
import './ItemCreate.css';

const ServiceCreate = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    hourly_rate: '',
    experience_years: '1',
    location: '',
    certifications: '',
    category_id: '',
  });

  const { data: categoriesData } = useQuery({
    queryKey: ['service-categories'],
    queryFn: async () => {
      const response = await serviceCategoryApi.list();
      const data = response.data as any;
      return Array.isArray(data) ? data : data?.results ?? [];
    },
  });

  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const response = await serviceApi.create(data as any);
      return response.data;
    },
    onSuccess: (data) => {
      navigate(`/services/${data.id}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="item-create">
      <div className="form-container">
        <h1>Offer a New Service</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Title</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={5}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="hourly_rate">Hourly Rate ($)</label>
              <input
                type="number"
                id="hourly_rate"
                name="hourly_rate"
                value={formData.hourly_rate}
                onChange={handleChange}
                step="0.01"
                min="0"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="experience_years">Years of Experience</label>
              <input
                type="number"
                id="experience_years"
                name="experience_years"
                value={formData.experience_years}
                onChange={handleChange}
                min="0"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="category_id">Category</label>
            <select
              id="category_id"
              name="category_id"
              value={formData.category_id}
              onChange={handleChange}
              required
            >
              <option value="">Select a category</option>
              {categoriesData?.map((category: { id: number; name: string }) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="location">Location</label>
            <input
              type="text"
              id="location"
              name="location"
              value={formData.location}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="certifications">Certifications (optional)</label>
            <textarea
              id="certifications"
              name="certifications"
              value={formData.certifications}
              onChange={handleChange}
              rows={2}
              placeholder="e.g. CompTIA A+, Apple Certified Mac Technician"
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={createMutation.isPending}>
            {createMutation.isPending ? 'Creating...' : 'List Service'}
          </button>
          {createMutation.isError && (
            <p style={{ color: '#b91c1c', fontSize: '0.875rem', marginTop: '0.75rem' }}>
              Couldn't create service. Please check the form and try again.
            </p>
          )}
        </form>
      </div>
    </div>
  );
};

export default ServiceCreate;
