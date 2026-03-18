'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { subscription, tiers, invoices } from '../../lib/api';

interface Subscription {
  tier: string;
  status: string;
  current_period_start?: string;
  current_period_end?: string;
  cancel_at_period_end: boolean;
}

interface Tier {
  name: string;
  price: number;
  requests: string;
  rate_limit: string;
  features: string[];
}

interface Invoice {
  id: number;
  amount: number;
  currency: string;
  status: string;
  created_at: string;
  invoice_url?: string;
}

export default function SubscriptionPage() {
  const router = useRouter();
  
  const [subscriptionData, setSubscriptionData] = useState<Subscription | null>(null);
  const [tierList, setTierList] = useState<Tier[]>([]);
  const [invoiceList, setInvoiceList] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingCheckout, setLoadingCheckout] = useState<string | null>(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

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
      const [sub, tiersData, invoicesData] = await Promise.all([
        subscription.get().catch(() => null),
        tiers.list(),
        invoices.list().catch(() => []),
      ]);
      
      setSubscriptionData(sub);
      setTierList(tiersData.tiers || []);
      setInvoiceList(invoicesData || []);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (tier: string) => {
    setError('');
    setLoadingCheckout(tier);

    try {
      const checkoutData = await subscription.createCheckout(tier);
      if (checkoutData.url) {
        window.location.href = checkoutData.url;
      } else {
        setMessage(`Upgraded to ${tier}!`);
        loadData();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create checkout session');
    } finally {
      setLoadingCheckout(null);
    }
  };

  const handleManageBilling = async () => {
    setLoading(true);
    try {
      const portalData = await subscription.createPortal();
      if (portalData.url) {
        window.location.href = portalData.url;
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to open billing portal');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel your subscription?')) {
      return;
    }

    setLoading(true);
    try {
      await subscription.cancel();
      setMessage('Subscription cancelled. You will retain access until the end of your billing period.');
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to cancel subscription');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString();
  };

  const formatCurrency = (amount: number, currency: string = 'usd') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).format(amount / 100);
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
        <h1 style={{ marginBottom: '2rem' }}>Subscription & Billing</h1>

        {error && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{error}</div>}
        {message && <div className="alert alert-success" style={{ marginBottom: '1rem' }}>{message}</div>}

        <div className="card" style={{ marginBottom: '2rem' }}>
          <h2 style={{ marginBottom: '1rem' }}>Current Plan</h2>
          
          {subscriptionData ? (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                <span style={{ 
                  fontSize: '1.5rem', 
                  fontWeight: 'bold',
                  textTransform: 'capitalize',
                  color: subscriptionData.tier === 'enterprise' ? '#9333ea' : 
                         subscriptionData.tier === 'pro' ? '#4f46e5' : '#6b7280'
                }}>
                  {subscriptionData.tier}
                </span>
                <span style={{
                  padding: '0.25rem 0.75rem',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  backgroundColor: subscriptionData.status === 'active' ? '#dcfce7' : '#fee2e2',
                  color: subscriptionData.status === 'active' ? '#166534' : '#991b1b',
                }}>
                  {subscriptionData.status}
                </span>
              </div>

              {subscriptionData.current_period_end && (
                <p style={{ color: 'var(--gray-600)', marginBottom: '1rem' }}>
                  {subscriptionData.cancel_at_period_end 
                    ? 'Cancels on ' 
                    : 'Renews on '}{formatDate(subscriptionData.current_period_end)}
                </p>
              )}

              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                <button 
                  onClick={handleManageBilling} 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  Manage Billing
                </button>
                {subscriptionData.tier !== 'free' && (
                  <button 
                    onClick={handleCancel} 
                    className="btn btn-secondary"
                    disabled={loading}
                  >
                    Cancel Subscription
                  </button>
                )}
              </div>
            </div>
          ) : (
            <p>Loading subscription info...</p>
          )}
        </div>

        <div className="card" style={{ marginBottom: '2rem' }}>
          <h2 style={{ marginBottom: '1.5rem' }}>Available Plans</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
            {tierList.map((tier) => {
              const isCurrentPlan = subscriptionData?.tier === tier.name.toLowerCase();
              const isUpgrade = !isCurrentPlan && 
                ((subscriptionData?.tier === 'free' && tier.name !== 'Free') ||
                 (subscriptionData?.tier === 'pro' && tier.name === 'Enterprise') ||
                 (subscriptionData?.tier === 'pro' && tier.name === 'Free'));

              return (
                <div 
                  key={tier.name}
                  style={{
                    border: isCurrentPlan ? '2px solid #9333ea' : '1px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '1.5rem',
                    backgroundColor: isCurrentPlan ? '#faf5ff' : 'white',
                  }}
                >
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                    {tier.name}
                  </h3>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                    ${tier.price}
                    {tier.price > 0 && <span style={{ fontSize: '0.875rem', fontWeight: 'normal' }}>/mo</span>}
                  </div>
                  <p style={{ color: 'var(--gray-600)', marginBottom: '1rem' }}>
                    {tier.requests} requests/month
                  </p>
                  <ul style={{ listStyle: 'none', padding: 0, marginBottom: '1.5rem' }}>
                    {tier.features.map((feature, i) => (
                      <li key={i} style={{ marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                        ✓ {feature}
                      </li>
                    ))}
                  </ul>
                  
                  {isCurrentPlan ? (
                    <button className="btn" disabled style={{ width: '100%', backgroundColor: '#e5e7eb' }}>
                      Current Plan
                    </button>
                  ) : tier.price > 0 ? (
                    <button 
                      onClick={() => handleUpgrade(tier.name.toLowerCase())}
                      className="btn btn-primary"
                      disabled={loadingCheckout === tier.name.toLowerCase()}
                      style={{ width: '100%' }}
                    >
                      {loadingCheckout === tier.name.toLowerCase() ? 'Loading...' : 
                       isUpgrade ? 'Upgrade' : 'Change Plan'}
                    </button>
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>

        <div className="card">
          <h2 style={{ marginBottom: '1.5rem' }}>Billing History</h2>
          
          {invoiceList.length > 0 ? (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #e5e7eb', textAlign: 'left' }}>
                  <th style={{ padding: '0.75rem 0' }}>Date</th>
                  <th style={{ padding: '0.75rem 0' }}>Amount</th>
                  <th style={{ padding: '0.75rem 0' }}>Status</th>
                  <th style={{ padding: '0.75rem 0' }}>Invoice</th>
                </tr>
              </thead>
              <tbody>
                {invoiceList.map((invoice) => (
                  <tr key={invoice.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={{ padding: '0.75rem 0' }}>{formatDate(invoice.created_at)}</td>
                    <td style={{ padding: '0.75rem 0' }}>{formatCurrency(invoice.amount, invoice.currency)}</td>
                    <td style={{ padding: '0.75rem 0' }}>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        backgroundColor: invoice.status === 'paid' ? '#dcfce7' : '#fef3c7',
                        color: invoice.status === 'paid' ? '#166534' : '#92400e',
                      }}>
                        {invoice.status}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem 0' }}>
                      {invoice.invoice_url && (
                        <a 
                          href={invoice.invoice_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          style={{ color: '#9333ea', textDecoration: 'underline' }}
                        >
                          Download
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{ color: 'var(--gray-600)' }}>No invoices yet.</p>
          )}
        </div>

        <div style={{ marginTop: '2rem' }}>
          <Link href="/dashboard" className="btn btn-secondary">Back to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}
