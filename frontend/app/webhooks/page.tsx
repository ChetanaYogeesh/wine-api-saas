'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { webhooks } from '../../lib/api';

interface Webhook {
  id: number;
  url: string;
  events: string;
  is_active: boolean;
  created_at: string;
}

const EVENT_OPTIONS = [
  { value: 'usage_threshold', label: 'Usage Threshold' },
  { value: 'api_limit_reached', label: 'API Limit Reached' },
  { value: 'new_user', label: 'New User' },
  { value: 'subscription_changed', label: 'Subscription Changed' },
];

export default function WebhooksPage() {
  const router = useRouter();
  
  const [webhookList, setWebhookList] = useState<Webhook[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [url, setUrl] = useState('');
  const [events, setEvents] = useState('usage_threshold');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    loadWebhooks();
  }, [router]);

  const loadWebhooks = async () => {
    try {
      const data = await webhooks.list();
      setWebhookList(data);
    } catch (err) {
      console.error('Failed to load webhooks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setCreating(true);

    try {
      await webhooks.create({ url, events });
      setSuccess('Webhook created successfully');
      setUrl('');
      setEvents('usage_threshold');
      setShowForm(false);
      loadWebhooks();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create webhook');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this webhook?')) {
      return;
    }

    try {
      await webhooks.delete(id);
      setSuccess('Webhook deleted');
      loadWebhooks();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete webhook');
    }
  };

  if (loading) {
    return (
      <div className="page">
        <div className="container">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1>Webhooks</h1>
          <button onClick={() => setShowForm(!showForm)} className="btn btn-primary">
            {showForm ? 'Cancel' : '+ Add Webhook'}
          </button>
        </div>

        {error && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{error}</div>}
        {success && <div className="alert alert-success" style={{ marginBottom: '1rem' }}>{success}</div>}

        {showForm && (
          <div className="card" style={{ marginBottom: '2rem' }}>
            <h2 style={{ marginBottom: '1rem' }}>Create Webhook</h2>
            <form onSubmit={handleCreate}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Webhook URL</label>
                <input
                  type="url"
                  className="input"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://your-server.com/webhook"
                  required
                  style={{ width: '100%', maxWidth: '500px' }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Events</label>
                <select
                  className="input"
                  value={events}
                  onChange={(e) => setEvents(e.target.value)}
                  style={{ width: '250px' }}
                >
                  {EVENT_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <button type="submit" className="btn btn-primary" disabled={creating}>
                {creating ? 'Creating...' : 'Create Webhook'}
              </button>
            </form>
          </div>
        )}

        <div className="card">
          <h2 style={{ marginBottom: '1.5rem' }}>Your Webhooks</h2>
          
          {webhookList.length === 0 ? (
            <p style={{ color: 'var(--gray-500)' }}>
              No webhooks configured. Create one to receive event notifications.
            </p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #e5e7eb', textAlign: 'left' }}>
                  <th style={{ padding: '0.75rem 0' }}>URL</th>
                  <th style={{ padding: '0.75rem 0' }}>Events</th>
                  <th style={{ padding: '0.75rem 0' }}>Status</th>
                  <th style={{ padding: '0.75rem 0' }}>Created</th>
                  <th style={{ padding: '0.75rem 0' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {webhookList.map((webhook) => (
                  <tr key={webhook.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={{ padding: '0.75rem 0' }}>
                      <code style={{ fontSize: '0.875rem' }}>{webhook.url}</code>
                    </td>
                    <td style={{ padding: '0.75rem 0' }}>
                      {EVENT_OPTIONS.find(o => o.value === webhook.events)?.label || webhook.events}
                    </td>
                    <td style={{ padding: '0.75rem 0' }}>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        backgroundColor: webhook.is_active ? '#dcfce7' : '#f3f4f6',
                        color: webhook.is_active ? '#166534' : '#6b7280',
                      }}>
                        {webhook.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem 0' }}>
                      {new Date(webhook.created_at).toLocaleDateString()}
                    </td>
                    <td style={{ padding: '0.75rem 0' }}>
                      <button
                        onClick={() => handleDelete(webhook.id)}
                        className="btn"
                        style={{ 
                          backgroundColor: '#fee2e2', 
                          color: '#991b1b',
                          padding: '0.25rem 0.75rem',
                          fontSize: '0.875rem'
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div style={{ marginTop: '2rem' }}>
          <Link href="/dashboard" className="btn btn-secondary">Back to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}
