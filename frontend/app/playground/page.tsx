'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiKeys, usage, tiers } from '../../lib/api';

interface APIKey {
  id: number;
  key: string;
  name: string;
  tier: string;
  is_active: boolean;
}

interface RequestExample {
  method: string;
  endpoint: string;
  description: string;
  params?: string;
}

const REQUEST_EXAMPLES: RequestExample[] = [
  { method: 'GET', endpoint: '/wines', description: 'List all wines' },
  { method: 'GET', endpoint: '/wines/1', description: 'Get wine by ID' },
  { method: 'GET', endpoint: '/wines/search?q=pinot', description: 'Search wines' },
  { method: 'GET', endpoint: '/wines/top-rated', description: 'Top rated wines' },
  { method: 'GET', endpoint: '/wines/stats', description: 'Wine statistics' },
  { method: 'GET', endpoint: '/regions', description: 'List regions' },
  { method: 'GET', endpoint: '/varieties', description: 'List varieties' },
];

export default function PlaygroundPage() {
  const router = useRouter();
  const [apiKeyList, setApiKeyList] = useState<APIKey[]>([]);
  const [selectedKey, setSelectedKey] = useState<string>('');
  const [selectedExample, setSelectedExample] = useState<RequestExample>(REQUEST_EXAMPLES[0]);
  const [customEndpoint, setCustomEndpoint] = useState('');
  const [customMethod, setCustomMethod] = useState('GET');
  const [customParams, setCustomParams] = useState('');
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [baseUrl, setBaseUrl] = useState('http://localhost:8000');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    loadApiKeys();
  }, [router]);

  const loadApiKeys = async () => {
    try {
      const keys = await apiKeys.list();
      setApiKeyList(keys);
      if (keys.length > 0) {
        setSelectedKey(keys[0].key);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const executeRequest = async () => {
    if (!selectedKey) {
      setError('Please select an API key');
      return;
    }

    setLoading(true);
    setError('');
    setResponse(null);

    const endpoint = customEndpoint || selectedExample.endpoint;
    const url = `${baseUrl}${endpoint}${customParams ? `?${customParams}` : ''}`;

    try {
      const res = await fetch(url, {
        method: customMethod,
        headers: {
          'X-API-Key': selectedKey,
          'Content-Type': 'application/json',
        },
      });

      const data = await res.json();
      setResponse({
        status: res.status,
        statusText: res.statusText,
        headers: Object.fromEntries(res.headers.entries()),
        data,
      });
    } catch (err: any) {
      setError(err.message || 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  const getMethodColor = (method: string) => {
    const colors: Record<string, string> = {
      GET: '#22c55e',
      POST: '#3b82f6',
      PUT: '#f59e0b',
      PATCH: '#8b5cf6',
      DELETE: '#ef4444',
    };
    return colors[method] || '#6b7280';
  };

  return (
    <div className="playground-page">
      <div className="container" style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
        <h1 style={{ marginBottom: '0.5rem' }}>API Playground</h1>
        <p style={{ color: '#666', marginBottom: '2rem' }}>
          Test the Wine API with your API keys. Select an endpoint and execute requests.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
          {/* Left Panel - Configuration */}
          <div>
            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Configuration</h3>
              
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  API Key
                </label>
                <select
                  className="input"
                  value={selectedKey}
                  onChange={(e) => setSelectedKey(e.target.value)}
                  style={{ width: '100%' }}
                >
                  <option value="">Select API Key</option>
                  {apiKeyList.map((key) => (
                    <option key={key.id} value={key.key}>
                      {key.name} ({key.tier})
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Base URL
                </label>
                <input
                  type="text"
                  className="input"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  style={{ width: '100%' }}
                  placeholder="http://localhost:8000"
                />
              </div>
            </div>

            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Example Requests</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {REQUEST_EXAMPLES.map((example, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setSelectedExample(example);
                      setCustomEndpoint('');
                    }}
                    style={{
                      padding: '0.75rem',
                      textAlign: 'left',
                      background: selectedExample === example ? 'var(--primary)' : 'var(--gray-100)',
                      color: selectedExample === example ? 'white' : 'var(--gray-800)',
                      border: 'none',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      fontFamily: 'monospace',
                      fontSize: '0.875rem',
                    }}
                  >
                    <span style={{ color: getMethodColor(example.method), fontWeight: 'bold' }}>
                      {example.method}
                    </span>{' '}
                    {example.description}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Panel - Request Builder */}
          <div>
            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Custom Request</h3>
              
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                <select
                  className="input"
                  value={customMethod}
                  onChange={(e) => setCustomMethod(e.target.value)}
                  style={{ width: '120px' }}
                >
                  <option value="GET">GET</option>
                  <option value="POST">POST</option>
                  <option value="PUT">PUT</option>
                  <option value="PATCH">PATCH</option>
                  <option value="DELETE">DELETE</option>
                </select>
                <input
                  type="text"
                  className="input"
                  value={customEndpoint}
                  onChange={(e) => setCustomEndpoint(e.target.value)}
                  placeholder="/wines?region=Napa Valley"
                  style={{ flex: 1 }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Query Parameters (optional)
                </label>
                <input
                  type="text"
                  className="input"
                  value={customParams}
                  onChange={(e) => setCustomParams(e.target.value)}
                  placeholder="region=Napa%20Valley&variety=Red%20Wine"
                  style={{ width: '100%' }}
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <button
                  className="btn btn-primary"
                  onClick={executeRequest}
                  disabled={loading || !selectedKey}
                  style={{ flex: 1 }}
                >
                  {loading ? 'Sending...' : 'Send Request'}
                </button>
                
                <span style={{ color: '#666', fontSize: '0.875rem' }}>
                  Using: {customEndpoint || selectedExample.endpoint}
                </span>
              </div>
            </div>

            {error && (
              <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>
                {error}
              </div>
            )}

            {response && (
              <div className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h3>Response</h3>
                  <span
                    style={{
                      padding: '0.25rem 0.75rem',
                      borderRadius: '0.25rem',
                      background: response.status >= 200 && response.status < 300 ? '#dcfce7' : '#fee2e2',
                      color: response.status >= 200 && response.status < 300 ? '#166534' : '#991b1b',
                      fontWeight: 'bold',
                    }}
                  >
                    {response.status} {response.statusText}
                  </span>
                </div>
                
                <div style={{ marginBottom: '1rem' }}>
                  <h4 style={{ fontSize: '0.875rem', marginBottom: '0.5rem', color: '#666' }}>Response Headers</h4>
                  <pre
                    style={{
                      background: '#f8fafc',
                      padding: '1rem',
                      borderRadius: '0.5rem',
                      overflow: 'auto',
                      fontSize: '0.75rem',
                      maxHeight: '150px',
                    }}
                  >
                    {JSON.stringify(response.headers, null, 2)}
                  </pre>
                </div>

                <div>
                  <h4 style={{ fontSize: '0.875rem', marginBottom: '0.5rem', color: '#666' }}>Response Body</h4>
                  <pre
                    style={{
                      background: '#1e293b',
                      color: '#e2e8f0',
                      padding: '1rem',
                      borderRadius: '0.5rem',
                      overflow: 'auto',
                      fontSize: '0.875rem',
                      maxHeight: '400px',
                    }}
                  >
                    {JSON.stringify(response.data, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
