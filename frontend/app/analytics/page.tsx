'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { analytics } from '../../lib/api';

interface AnalyticsData {
  total_requests: number;
  requests_today: number;
  requests_this_month: number;
  avg_response_time_ms: number;
  usage_by_day: { date: string; count: number }[];
  usage_by_endpoint: { endpoint: string; count: number }[];
  usage_by_status: Record<string, number>;
}

export default function AnalyticsPage() {
  const router = useRouter();
  
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    loadAnalytics();
  }, [router, days]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const response = await analytics.get(days);
      setData(response);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'json' | 'csv') => {
    setExporting(true);
    try {
      const blob = await analytics.export(format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setExporting(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
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
          <h1>Analytics</h1>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <select
              className="input"
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              style={{ width: '150px' }}
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
            <button 
              onClick={() => handleExport('csv')} 
              className="btn btn-secondary"
              disabled={exporting}
            >
              Export CSV
            </button>
            <button 
              onClick={() => handleExport('json')} 
              className="btn btn-secondary"
              disabled={exporting}
            >
              Export JSON
            </button>
          </div>
        </div>

        {data && (
          <>
            <div className="stats-grid" style={{ marginBottom: '2rem' }}>
              <div className="card stat-card">
                <div className="stat-value">{formatNumber(data.total_requests)}</div>
                <div className="stat-label">Total Requests</div>
              </div>
              <div className="card stat-card">
                <div className="stat-value">{formatNumber(data.requests_today)}</div>
                <div className="stat-label">Today</div>
              </div>
              <div className="card stat-card">
                <div className="stat-value">{formatNumber(data.requests_this_month)}</div>
                <div className="stat-label">This Month</div>
              </div>
              <div className="card stat-card">
                <div className="stat-value">{data.avg_response_time_ms}ms</div>
                <div className="stat-label">Avg Response Time</div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
              <div className="card">
                <h2 style={{ marginBottom: '1rem' }}>Usage by Day</h2>
                {data.usage_by_day && data.usage_by_day.length > 0 ? (
                  <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    <table style={{ width: '100%', fontSize: '0.875rem' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                          <th style={{ textAlign: 'left', padding: '0.5rem 0' }}>Date</th>
                          <th style={{ textAlign: 'right', padding: '0.5rem 0' }}>Requests</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.usage_by_day.slice(-10).reverse().map((day, i) => (
                          <tr key={i} style={{ borderBottom: '1px solid #f3f4f6' }}>
                            <td style={{ padding: '0.5rem 0' }}>{day.date}</td>
                            <td style={{ textAlign: 'right', padding: '0.5rem 0' }}>{day.count.toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p style={{ color: 'var(--gray-500)' }}>No data available</p>
                )}
              </div>

              <div className="card">
                <h2 style={{ marginBottom: '1rem' }}>Usage by Endpoint</h2>
                {data.usage_by_endpoint && data.usage_by_endpoint.length > 0 ? (
                  <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    <table style={{ width: '100%', fontSize: '0.875rem' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                          <th style={{ textAlign: 'left', padding: '0.5rem 0' }}>Endpoint</th>
                          <th style={{ textAlign: 'right', padding: '0.5rem 0' }}>Requests</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.usage_by_endpoint.slice(0, 10).map((ep, i) => (
                          <tr key={i} style={{ borderBottom: '1px solid #f3f4f6' }}>
                            <td style={{ padding: '0.5rem 0' }}>
                              <code style={{ fontSize: '0.8rem', background: '#f3f4f6', padding: '0.125rem 0.375rem', borderRadius: '4px' }}>
                                {ep.endpoint}
                              </code>
                            </td>
                            <td style={{ textAlign: 'right', padding: '0.5rem 0' }}>{ep.count.toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p style={{ color: 'var(--gray-500)' }}>No data available</p>
                )}
              </div>

              <div className="card">
                <h2 style={{ marginBottom: '1rem' }}>Status Codes</h2>
                {data.usage_by_status && Object.keys(data.usage_by_status).length > 0 ? (
                  <div>
                    {Object.entries(data.usage_by_status).map(([status, count]) => (
                      <div key={status} style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        padding: '0.5rem 0',
                        borderBottom: '1px solid #f3f4f6'
                      }}>
                        <span>
                          <span style={{
                            display: 'inline-block',
                            width: '8px',
                            height: '8px',
                            borderRadius: '50%',
                            marginRight: '0.5rem',
                            backgroundColor: 
                              status.startsWith('2') ? '#22c55e' :
                              status.startsWith('4') ? '#f59e0b' :
                              status.startsWith('5') ? '#ef4444' : '#6b7280'
                          }} />
                          {status}
                        </span>
                        <span style={{ fontWeight: 'bold' }}>{count.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: 'var(--gray-500)' }}>No data available</p>
                )}
              </div>
            </div>
          </>
        )}

        <div style={{ marginTop: '2rem' }}>
          <Link href="/dashboard" className="btn btn-secondary">Back to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}
