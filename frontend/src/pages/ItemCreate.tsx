import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { itemApi, itemImageApi, categoryApi } from '../api/endpoints';
import './ItemCreate.css';

const ItemCreate = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    daily_price: '',
    condition: 'good',
    location: '',
    category_id: '',
  });
  const [images, setImages] = useState<File[]>([]);
  const [uploadingImages, setUploadingImages] = useState(false);

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await categoryApi.list();
      return response.data.results;
    },
  });

  const createMutation = useMutation({
    mutationFn: async (data: FormData) => {
      const response = await itemApi.create(data as any);
      return response.data;
    },
    onSuccess: async (data) => {
      if (images.length > 0) {
        setUploadingImages(true);
        try {
          await Promise.all(
            images.map((image, index) => itemImageApi.upload(data.id, image, index === 0))
          );
        } catch {
          // Item was created successfully; photo upload failures aren't fatal here.
        } finally {
          setUploadingImages(false);
        }
      }
      navigate(`/items/${data.id}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData as any);
  };

  const handleImagesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setImages([...images, ...Array.from(e.target.files ?? [])]);
    e.target.value = '';
  };

  const removeImage = (index: number) => {
    setImages(images.filter((_, i) => i !== index));
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
        <h1>List a New Item</h1>
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
              <label htmlFor="daily_price">Daily Price ($)</label>
              <input
                type="number"
                id="daily_price"
                name="daily_price"
                value={formData.daily_price}
                onChange={handleChange}
                step="0.01"
                min="0"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="condition">Condition</label>
              <select
                id="condition"
                name="condition"
                value={formData.condition}
                onChange={handleChange}
                required
              >
                <option value="excellent">Excellent</option>
                <option value="good">Good</option>
                <option value="fair">Fair</option>
                <option value="poor">Poor</option>
              </select>
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
              {categories?.map((category) => (
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
            <label htmlFor="images">Photos</label>
            <input
              type="file"
              id="images"
              accept="image/*"
              multiple
              onChange={handleImagesChange}
            />
            {images.length > 0 && (
              <ul className="image-preview-list">
                {images.map((image, index) => (
                  <li key={`${image.name}-${index}`}>
                    <span>{image.name}{index === 0 ? ' (primary)' : ''}</span>
                    <button type="button" onClick={() => removeImage(index)} aria-label={`Remove ${image.name}`}>
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={createMutation.isPending || uploadingImages}
          >
            {createMutation.isPending
              ? 'Creating...'
              : uploadingImages
              ? 'Uploading photos...'
              : 'Create Item'}
          </button>
          {createMutation.isError && (
            <p className="item-create-error">Couldn't create item. Please check the form and try again.</p>
          )}
        </form>
      </div>
    </div>
  );
};

export default ItemCreate;
