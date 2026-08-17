import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { kycApi } from '../api/endpoints';
import type { KYCVerification } from '../types';
import './KYCVerify.css';

const isSubmitted = (data: KYCVerification | { status: string } | undefined): data is KYCVerification =>
  !!data && 'id' in data;

const KYCVerify = () => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    legal_name: '',
    id_type: 'passport',
    id_number: '',
  });
  const [idDocument, setIdDocument] = useState<File | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['kyc-my-status'],
    queryFn: async () => (await kycApi.getMyStatus()).data,
  });

  const submitMutation = useMutation({
    mutationFn: async () => {
      const payload = new FormData();
      payload.append('legal_name', formData.legal_name);
      payload.append('id_type', formData.id_type);
      payload.append('id_number', formData.id_number);
      if (idDocument) payload.append('id_document', idDocument);
      const response = await kycApi.create(payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kyc-my-status'] });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submitMutation.mutate();
  };

  if (isLoading) return <div className="loading">Loading verification status...</div>;

  return (
    <div className="kyc-page">
      <div className="kyc-container">
        <h1>Identity Verification</h1>

        {isSubmitted(data) ? (
          <div className="kyc-status-card">
            <span className={`status-badge ${data.status}`}>{data.status}</span>
            <div className="kyc-status-details">
              <div className="kyc-detail-row">
                <strong>Legal name</strong>
                <span>{data.legal_name}</span>
              </div>
              <div className="kyc-detail-row">
                <strong>ID type</strong>
                <span style={{ textTransform: 'capitalize' }}>{data.id_type.replace('_', ' ')}</span>
              </div>
              <div className="kyc-detail-row">
                <strong>Submitted</strong>
                <span>{new Date(data.created_at).toLocaleDateString()}</span>
              </div>
              {data.status === 'rejected' && data.rejection_reason && (
                <div className="kyc-rejection-reason">
                  <strong>Reason for rejection</strong>
                  <p>{data.rejection_reason}</p>
                </div>
              )}
            </div>
            {data.status === 'pending' && (
              <p className="kyc-hint">Your submission is awaiting review. We'll notify you once it's processed.</p>
            )}
            {data.status === 'approved' && (
              <p className="kyc-hint">Your identity has been verified.</p>
            )}
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="kyc-form">
            <p className="kyc-intro">
              Verify your identity to build trust with other GearGo users. Submit your legal name, ID type,
              and a photo of your ID document.
            </p>

            <div className="form-group">
              <label htmlFor="legal_name">Legal Name</label>
              <input
                type="text"
                id="legal_name"
                value={formData.legal_name}
                onChange={(e) => setFormData({ ...formData, legal_name: e.target.value })}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="id_type">ID Type</label>
                <select
                  id="id_type"
                  value={formData.id_type}
                  onChange={(e) => setFormData({ ...formData, id_type: e.target.value })}
                  required
                >
                  <option value="passport">Passport</option>
                  <option value="driver_license">Driver License</option>
                  <option value="national_id">National ID</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="id_number">ID Number</label>
                <input
                  type="text"
                  id="id_number"
                  value={formData.id_number}
                  onChange={(e) => setFormData({ ...formData, id_number: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="id_document">ID Document Photo</label>
              <input
                type="file"
                id="id_document"
                accept="image/*"
                onChange={(e) => setIdDocument(e.target.files?.[0] ?? null)}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={submitMutation.isPending}>
              {submitMutation.isPending ? 'Submitting...' : 'Submit for Verification'}
            </button>
            {submitMutation.isError && (
              <p className="kyc-error">Couldn't submit verification. Please check the form and try again.</p>
            )}
          </form>
        )}

        <Link to="/profile" className="kyc-back-link">← Back to profile</Link>
      </div>
    </div>
  );
};

export default KYCVerify;
