'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiKeys, usage, tiers } from '../../lib/api';

interface APIKey {
  id: number;
  key: string;
  name: string;
  tier: string;
  is_active: boolean;
  rate_limit: number;
  monthly_limit: number;
  created_at: string;
}

interface UsageStats {
  total_requests: number;
  requests_today: number;
  requests_this_month: number;
  avg_response_time_ms: number;
  top_endpoints: { endpoint: string; count: number }[];
  requests_by_status: Record<string, number>;
}

export default function DashboardPage() {
  const router = useRouter();
  const [apiKeyList, setApiKeyList] = useState<APIKey[]>([]);
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);
  const [tierList, setTierList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyTier, setNewKeyTier] = useState('free');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    loadData();
  }, [router]);

  const loadData = async () => {
    try {
      const [keys, stats, tiersData] = await Promise.all([
        apiKeys.list(),
        usage.getStats(),
        tiers.list(),
      ]);
      setApiKeyList(keys);
      setUsageStats(stats);
      setTierList(tiersData.tiers);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const createApiKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      const newKey = await apiKeys.create(newKeyName, newKeyTier);
      setApiKeyList([...apiKeyList, newKey]);
      setNewKeyName('');
      setNewKeyTier('free');
    } catch (err) {
      console.error(err);
    } finally {
      setCreating(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    router.push('/');
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      alert('Copied to clipboard!');
    } catch (err) {
      console.error('Failed to copy:', err);
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      alert('Copied to clipboard!');
    }
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="container" style={{ padding: '4rem', textAlign: 'center' }}>
          Loading...
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Link href="/" className="navbar-brand">🍷 Wine API</Link>
          <button onClick={logout} className="btn btn-secondary">Logout</button>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="container">
          <h1 style={{ marginBottom: '2rem' }}>Dashboard</h1>

          {/* Usage Stats */}
          {usageStats && (
            <div className="stats-grid">
              <div className="card stat-card">
                <div className="stat-value">{usageStats.total_requests.toLocaleString()}</div>
                <div className="stat-label">Total Requests</div>
              </div>
              <div className="card stat-card">
                <div className="stat-value">{usageStats.requests_today.toLocaleString()}</div>
                <div className="stat-label">Requests Today</div>
              </div>
              <div className="card stat-card">
                <div className="stat-value">{usageStats.requests_this_month.toLocaleString()}</div>
                <div className="stat-label">This Month</div>
              </div>
              <div className="card stat-card">
                <div className="stat-value">{usageStats.avg_response_time_ms}ms</div>
                <div className="stat-label">Avg Response Time</div>
              </div>
            </div>
          )}

          {/* Create API Key */}
          <div className="card" style={{ marginBottom: '2rem' }}>
            <h2 style={{ marginBottom: '1rem' }}>Create New API Key</h2>
            <form onSubmit={createApiKey} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              <input
                type="text"
                className="input"
                placeholder="Key name (e.g., My App)"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                style={{ flex: '1', minWidth: '200px' }}
                required
              />
              <select
                className="input"
                value={newKeyTier}
                onChange={(e) => setNewKeyTier(e.target.value)}
                style={{ width: '150px' }}
              >
                {tierList.map((tier) => (
                  <option key={tier.name} value={tier.name}>
                    {tier.name.charAt(0).toUpperCase() + tier.name.slice(1)}
                  </option>
                ))}
              </select>
              <button type="submit" className="btn btn-primary" disabled={creating}>
                {creating ? 'Creating...' : 'Create Key'}
              </button>
            </form>
          </div>

          {/* API Keys */}
          <div className="card">
            <h2 style={{ marginBottom: '1rem' }}>Your API Keys</h2>
            {apiKeyList.length === 0 ? (
              <p style={{ color: 'var(--gray-500)' }}>No API keys yet. Create one above.</p>
            ) : (
              <table className="api-keys-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Tier</th>
                    <th>API Key</th>
                    <th>Rate Limit</th>
                    <th>Monthly Limit</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {apiKeyList.map((key) => (
                    <tr key={key.id}>
                      <td>{key.name}</td>
                      <td>
                        <span className={`tier-badge tier-${key.tier}`}>
                          {key.tier}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <code style={{ fontSize: '0.875rem', background: 'var(--gray-100)', padding: '0.25rem 0.5rem', borderRadius: '0.25rem' }}>
                            {key.key.substring(0, 20)}...
                          </code>
                          <button
                            onClick={() => copyToClipboard(key.key)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1rem' }}
                            title="Copy to clipboard"
                          >
                            📋
                          </button>
                        </div>
                      </td>
                      <td>{key.rate_limit ?? 0}/min</td>
                      <td>{(key.monthly_limit ?? 0).toLocaleString()}</td>
                      <td>{key.created_at ? new Date(key.created_at).toLocaleDateString() : 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Example Usage */}
          <div className="card" style={{ marginTop: '2rem' }}>
            <h2 style={{ marginBottom: '1rem' }}>Example Usage</h2>
            <p style={{ marginBottom: '1rem', color: 'var(--gray-600)' }}>
              Use your API key in the <code>X-API-Key</code> header:
            </p>
            <pre className="code-block">
{`curl -H "X-API-Key: YOUR_API_KEY" \\
  "http://localhost:8000/wines?limit=10"`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
