'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { whiteLabel } from '../../lib/api';

interface WhiteLabelConfig {
  id?: number;
  company_name?: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  custom_domain?: string;
  email_footer?: string;
  is_active?: boolean;
  ssl_enabled?: boolean;
}

export default function WhiteLabelPage() {
  const router = useRouter();
  
  const [config, setConfig] = useState<WhiteLabelConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [companyName, setCompanyName] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [primaryColor, setPrimaryColor] = useState('#9333ea');
  const [secondaryColor, setSecondaryColor] = useState('#4f46e5');
  const [customDomain, setCustomDomain] = useState('');
  const [emailFooter, setEmailFooter] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    loadConfig();
  }, [router]);

  const loadConfig = async () => {
    try {
      const data = await whiteLabel.get();
      setConfig(data);
      setCompanyName(data.company_name || '');
      setLogoUrl(data.logo_url || '');
      setPrimaryColor(data.primary_color || '#9333ea');
      setSecondaryColor(data.secondary_color || '#4f46e5');
      setCustomDomain(data.custom_domain || '');
      setEmailFooter(data.email_footer || '');
    } catch (err) {
      console.error('Failed to load config:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);

    try {
      if (config?.id) {
        await whiteLabel.update({
          company_name: companyName,
          logo_url: logoUrl,
          primary_color: primaryColor,
          secondary_color: secondaryColor,
          email_footer: emailFooter,
        });
      } else {
        await whiteLabel.create({
          company_name: companyName,
          logo_url: logoUrl,
          primary_color: primaryColor,
          secondary_color: secondaryColor,
          custom_domain: customDomain,
          email_footer: emailFooter,
        });
      }
      setSuccess('Settings saved successfully');
      loadConfig();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete white-label configuration?')) {
      return;
    }

    try {
      await whiteLabel.delete();
      setSuccess('White-label configuration deleted');
      setConfig(null);
      setCompanyName('');
      setLogoUrl('');
      setPrimaryColor('#9333ea');
      setSecondaryColor('#4f46e5');
      setCustomDomain('');
      setEmailFooter('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete configuration');
    }
  };

  const handleVerifyDomain = async () => {
    if (!customDomain) {
      setError('Please enter a custom domain first');
      return;
    }

    try {
      const result = await whiteLabel.verifyDomain(customDomain);
      if (result.verified) {
        setSuccess(`Domain ${customDomain} verified successfully!`);
      } else {
        setError(`Please add the CNAME record: ${result.cname_record}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to verify domain');
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
        <h1 style={{ marginBottom: '2rem' }}>White-Label Configuration</h1>

        {error && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{error}</div>}
        {success && <div className="alert alert-success" style={{ marginBottom: '1rem' }}>{success}</div>}

        <form onSubmit={handleSave}>
          <div className="card" style={{ marginBottom: '2rem' }}>
            <h2 style={{ marginBottom: '1.5rem' }}>Branding</h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Company Name</label>
                <input
                  type="text"
                  className="input"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="My Wine Company"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Logo URL</label>
                <input
                  type="url"
                  className="input"
                  value={logoUrl}
                  onChange={(e) => setLogoUrl(e.target.value)}
                  placeholder="https://example.com/logo.png"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Primary Color</label>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <input
                    type="color"
                    value={primaryColor}
                    onChange={(e) => setPrimaryColor(e.target.value)}
                    style={{ width: '50px', height: '40px', border: 'none', cursor: 'pointer' }}
                  />
                  <input
                    type="text"
                    className="input"
                    value={primaryColor}
                    onChange={(e) => setPrimaryColor(e.target.value)}
                    placeholder="#9333ea"
                    style={{ flex: 1 }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Secondary Color</label>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <input
                    type="color"
                    value={secondaryColor}
                    onChange={(e) => setSecondaryColor(e.target.value)}
                    style={{ width: '50px', height: '40px', border: 'none', cursor: 'pointer' }}
                  />
                  <input
                    type="text"
                    className="input"
                    value={secondaryColor}
                    onChange={(e) => setSecondaryColor(e.target.value)}
                    placeholder="#4f46e5"
                    style={{ flex: 1 }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="card" style={{ marginBottom: '2rem' }}>
            <h2 style={{ marginBottom: '1.5rem' }}>Custom Domain</h2>
            <p style={{ marginBottom: '1rem', color: 'var(--gray-600)', fontSize: '0.875rem' }}>
              Configure a custom domain for your API (requires Enterprise plan)
            </p>
            
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Custom Domain</label>
                <input
                  type="text"
                  className="input"
                  value={customDomain}
                  onChange={(e) => setCustomDomain(e.target.value)}
                  placeholder="api.yourdomain.com"
                  disabled={!!config?.id}
                  style={{ width: '100%' }}
                />
              </div>
              {config?.id && (
                <button
                  type="button"
                  onClick={handleVerifyDomain}
                  className="btn btn-secondary"
                >
                  Verify Domain
                </button>
              )}
            </div>

            {config?.is_active !== undefined && (
              <div style={{ marginTop: '1rem' }}>
                <span style={{
                  padding: '0.25rem 0.75rem',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  backgroundColor: config.is_active ? '#dcfce7' : '#f3f4f6',
                  color: config.is_active ? '#166534' : '#6b7280',
                }}>
                  {config.is_active ? 'Active' : 'Inactive'}
                </span>
                {config.ssl_enabled && (
                  <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', color: '#166534' }}>
                    SSL Enabled
                  </span>
                )}
              </div>
            )}
          </div>

          <div className="card" style={{ marginBottom: '2rem' }}>
            <h2 style={{ marginBottom: '1.5rem' }}>Email Footer</h2>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>Custom Footer Text</label>
              <textarea
                className="input"
                value={emailFooter}
                onChange={(e) => setEmailFooter(e.target.value)}
                placeholder="© 2026 My Wine Company. All rights reserved."
                rows={3}
                style={{ width: '100%', resize: 'vertical' }}
              />
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
            {config?.id && (
              <button
                type="button"
                onClick={handleDelete}
                className="btn"
                style={{ backgroundColor: '#fee2e2', color: '#991b1b' }}
              >
                Delete Configuration
              </button>
            )}
          </div>
        </form>

        <div style={{ marginTop: '2rem' }}>
          <Link href="/dashboard" className="btn btn-secondary">Back to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}
