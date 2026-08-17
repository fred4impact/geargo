import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { kycApi } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import './KYCReview.css';

const KYCReview = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [rejectingId, setRejectingId] = useState<number | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['kyc-review-list'],
    queryFn: async () => (await kycApi.list()).data,
    enabled: !!user?.user?.is_staff,
  });

  const approveMutation = useMutation({
    mutationFn: (id: number) => kycApi.approve(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['kyc-review-list'] }),
  });

  const rejectMutation = useMutation({
    mutationFn: ({ id, reason }: { id: number; reason: string }) => kycApi.reject(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kyc-review-list'] });
      setRejectingId(null);
      setRejectionReason('');
    },
  });

  if (!user?.user?.is_staff) {
    return (
      <div className="kyc-review-page">
        <p className="no-access">Staff access only.</p>
      </div>
    );
  }

  if (isLoading) return <div className="loading">Loading submissions...</div>;

  const submissions = data?.results ?? [];
  const pending = submissions.filter((s) => s.status === 'pending');
  const reviewed = submissions.filter((s) => s.status !== 'pending');

  return (
    <div className="kyc-review-page">
      <h1>KYC Review</h1>

      <section>
        <h2>Pending ({pending.length})</h2>
        {pending.length === 0 ? (
          <p className="no-items-hint">No submissions awaiting review.</p>
        ) : (
          <div className="kyc-review-list">
            {pending.map((kyc) => (
              <div key={kyc.id} className="kyc-review-card">
                <div className="kyc-review-main">
                  <img src={kyc.id_document_url} alt="ID document" className="kyc-review-image" />
                  <div className="kyc-review-info">
                    <h3>{kyc.legal_name}</h3>
                    <p>{kyc.profile.full_name} ({kyc.profile.user.email})</p>
                    <p style={{ textTransform: 'capitalize' }}>{kyc.id_type.replace('_', ' ')} — {kyc.id_number}</p>
                    <p className="kyc-review-date">Submitted {new Date(kyc.created_at).toLocaleDateString()}</p>
                  </div>
                </div>

                {rejectingId === kyc.id ? (
                  <div className="kyc-reject-form">
                    <textarea
                      placeholder="Reason for rejection"
                      value={rejectionReason}
                      onChange={(e) => setRejectionReason(e.target.value)}
                      rows={2}
                    />
                    <div className="kyc-review-actions">
                      <button
                        type="button"
                        className="btn btn-primary"
                        disabled={!rejectionReason.trim() || rejectMutation.isPending}
                        onClick={() => rejectMutation.mutate({ id: kyc.id, reason: rejectionReason })}
                      >
                        Confirm Reject
                      </button>
                      <button type="button" className="btn btn-secondary" onClick={() => setRejectingId(null)}>
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="kyc-review-actions">
                    <button
                      type="button"
                      className="btn btn-primary"
                      disabled={approveMutation.isPending}
                      onClick={() => approveMutation.mutate(kyc.id)}
                    >
                      Approve
                    </button>
                    <button type="button" className="btn btn-secondary" onClick={() => setRejectingId(kyc.id)}>
                      Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {reviewed.length > 0 && (
        <section>
          <h2>Reviewed ({reviewed.length})</h2>
          <div className="kyc-review-list">
            {reviewed.map((kyc) => (
              <div key={kyc.id} className="kyc-review-card kyc-review-card-compact">
                <div className="kyc-review-main">
                  <div className="kyc-review-info">
                    <h3>{kyc.legal_name}</h3>
                    <p>{kyc.profile.full_name} ({kyc.profile.user.email})</p>
                  </div>
                </div>
                <span className={`status-badge ${kyc.status}`}>{kyc.status}</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};

export default KYCReview;
