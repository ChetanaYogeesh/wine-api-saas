'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { user, apiKeys } from '../../lib/api';

interface UserProfile {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

interface APIKey {
  id: number;
  name: string;
  tier: string;
  is_active: boolean;
  created_at: string;
}

export default function ProfilePage() {
  const router = useRouter();
  
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [apiKeysList, setApiKeysList] = useState<APIKey[]>([]);
  const [loading, setLoading] = useState(true);

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
      const [profileData, keys] = await Promise.all([
        user.getProfile(),
        apiKeys.list(),
      ]);
      setProfile(profileData);
      setApiKeysList(keys);
    } catch (err) {
      console.error('Failed to load profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/');
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
          <h1>My Profile</h1>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>

        <div className="card" style={{ marginBottom: '2rem' }}>
          <h2 style={{ marginBottom: '1.5rem' }}>Account Information</h2>
          
          <div style={{ display: 'grid', gap: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '1rem', borderBottom: '1px solid var(--gray-200)' }}>
              <span style={{ color: 'var(--gray-600)' }}>Full Name</span>
              <span style={{ fontWeight: '500' }}>{profile?.full_name || 'Not set'}</span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '1rem', borderBottom: '1px solid var(--gray-200)' }}>
              <span style={{ color: 'var(--gray-600)' }}>Email</span>
              <span style={{ fontWeight: '500' }}>{profile?.email}</span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '1rem', borderBottom: '1px solid var(--gray-200)' }}>
              <span style={{ color: 'var(--gray-600)' }}>Account Status</span>
              <span>
                <span className={`status-badge ${profile?.is_verified ? 'status-active' : 'status-pending'}`}>
                  {profile?.is_verified ? 'Verified' : 'Pending Verification'}
                </span>
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '1rem', borderBottom: '1px solid var(--gray-200)' }}>
              <span style={{ color: 'var(--gray-600)' }}>Member Since</span>
              <span style={{ fontWeight: '500' }}>
                {profile?.created_at ? new Date(profile.created_at).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                }) : 'N/A'}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--gray-600)' }}>Account ID</span>
              <span style={{ fontWeight: '500', fontFamily: 'monospace' }}>#{profile?.id}</span>
            </div>
          </div>
        </div>

        <div className="card" style={{ marginBottom: '2rem' }}>
          <h2 style={{ marginBottom: '1.5rem' }}>API Keys</h2>
          
          {apiKeysList.length === 0 ? (
            <p style={{ color: 'var(--gray-500)' }}>No API keys yet.</p>
          ) : (
            <div style={{ display: 'grid', gap: '0.75rem' }}>
              {apiKeysList.map((key) => (
                <div key={key.id} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '0.75rem',
                  background: 'var(--gray-100)',
                  borderRadius: '0.5rem'
                }}>
                  <div>
                    <div style={{ fontWeight: '500' }}>{key.name}</div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)' }}>
                      Created {new Date(key.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <span className={`tier-badge tier-${key.tier}`}>{key.tier}</span>
                </div>
              ))}
            </div>
          )}
          
          <div style={{ marginTop: '1rem' }}>
            <Link href="/dashboard" className="btn btn-primary">Manage API Keys</Link>
          </div>
        </div>

        <div className="card">
          <h2 style={{ marginBottom: '1rem' }}>Quick Links</h2>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <Link href="/dashboard" className="btn btn-secondary">Dashboard</Link>
            <Link href="/settings" className="btn btn-secondary">Account Settings</Link>
            <Link href="/analytics" className="btn btn-secondary">View Analytics</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
