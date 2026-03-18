'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { usageAlerts } from '../../lib/api';

interface UsageAlert {
  id: number;
  threshold_percent: number;
  email: string;
  is_active: boolean;
  last_sent_at?: string;
  created_at: string;
}

export default function UsageAlertsPage() {
  const router = useRouter();
  
  const [alerts, setAlerts] = useState<UsageAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [thresholdPercent, setThresholdPercent] = useState('80');
  const [email, setEmail] = useState('');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    loadAlerts();
  }, [router]);

  const loadAlerts = async () => {
    try {
      const data = await usageAlerts.list();
      setAlerts(data);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setCreating(true);

    try {
      await usageAlerts.create({
        threshold_percent: parseInt(thresholdPercent),
        email,
      });
      setSuccess('Alert created successfully');
      setThresholdPercent('80');
      setEmail('');
      setShowForm(false);
      loadAlerts();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create alert');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this alert?')) {
      return;
    }

    try {
      await usageAlerts.delete(id);
      setSuccess('Alert deleted');
      loadAlerts();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete alert');
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
          <h1>Usage Alerts</h1>
          <button onClick={() => setShowForm(!showForm)} className="btn btn-primary">
            {showForm ? 'Cancel' : '+ Add Alert'}
          </button>
        </div>

        {error && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{error}</div>}
        {success && <div className="alert alert-success" style={{ marginBottom: '1rem' }}>{success}</div>}

        {showForm && (
          <div className="card" style={{ marginBottom: '2rem' }}>
            <h2 style={{ marginBottom: '1rem' }}>Create Usage Alert</h2>
            <p style={{ marginBottom: '1rem', color: 'var(--gray-600)', fontSize: '0.875rem' }}>
              Get notified when your API usage reaches a certain percentage of your monthly limit.
            </p>
            <form onSubmit={handleCreate}>
              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem' }}>Alert at</label>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <input
                      type="number"
                      className="input"
                      value={thresholdPercent}
                      onChange={(e) => setThresholdPercent(e.target.value)}
                      min="1"
                      max="100"
                      required
                      style={{ width: '100px' }}
                    />
                    <span style={{ marginLeft: '0.5rem' }}>% of limit</span>
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem' }}>Email</label>
                  <input
                    type="email"
                    className="input"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="alerts@example.com"
                    required
                    style={{ width: '250px' }}
                  />
                </div>

                <button type="submit" className="btn btn-primary" disabled={creating}>
                  {creating ? 'Creating...' : 'Create Alert'}
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="card">
          <h2 style={{ marginBottom: '1.5rem' }}>Your Alerts</h2>
          
          {alerts.length === 0 ? (
            <p style={{ color: 'var(--gray-500)' }}>
              No alerts configured. Create one to get notified when you're approaching your usage limit.
            </p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #e5e7eb', textAlign: 'left' }}>
                  <th style={{ padding: '0.75rem 0' }}>Threshold</th>
                  <th style={{ padding: '0.75rem 0' }}>Email</th>
                  <th style={{ padding: '0.75rem 0' }}>Status</th>
                  <th style={{ padding: '0.75rem 0' }}>Last Sent</th>
                  <th style={{ padding: '0.75rem 0' }}>Created</th>
                  <th style={{ padding: '0.75rem 0' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert) => (
                  <tr key={alert.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={{ padding: '0.75rem 0' }}>
                      <strong>{alert.threshold_percent}%</strong>
                    </td>
                    <td style={{ padding: '0.75rem 0' }}>{alert.email}</td>
                    <td style={{ padding: '0.75rem 0' }}>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        backgroundColor: alert.is_active ? '#dcfce7' : '#f3f4f6',
                        color: alert.is_active ? '#166534' : '#6b7280',
                      }}>
                        {alert.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem 0' }}>
                      {alert.last_sent_at 
                        ? new Date(alert.last_sent_at).toLocaleString()
                        : 'Never'
                      }
                    </td>
                    <td style={{ padding: '0.75rem 0' }}>
                      {new Date(alert.created_at).toLocaleDateString()}
                    </td>
                    <td style={{ padding: '0.75rem 0' }}>
                      <button
                        onClick={() => handleDelete(alert.id)}
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
