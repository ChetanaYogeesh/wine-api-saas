'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { auth } from '../../lib/api';

function sanitizeInput(input: string): string {
  return input.trim();
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const sanitizedEmail = sanitizeInput(email);

    if (!sanitizedEmail || !password) {
      setError('Please enter both email and password');
      return;
    }

    setLoading(true);

    try {
      const data = await auth.login(sanitizedEmail, password);
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        router.push('/dashboard');
      } else {
        setError('Login failed. Please try again.');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Invalid email or password';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="card auth-card">
        <h1>Login</h1>
        
        {error && <div className="alert alert-error">{error}</div>}
        
        <form className="auth-form" onSubmit={handleSubmit}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Email</label>
            <input
              type="email"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              maxLength={254}
              autoComplete="email"
            />
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Password</label>
            <input
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <p style={{ textAlign: 'center', marginTop: '1rem' }}>
          <Link href="/forgot-password" style={{ fontSize: '0.875rem' }}>
            Forgot password?
          </Link>
        </p>
        
        <p className="auth-footer">
          Don&apos;t have an account? <Link href="/register">Sign up</Link>
        </p>
      </div>
    </div>
  );
}
