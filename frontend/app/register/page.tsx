'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { auth } from '../../lib/api';

function sanitizeInput(input: string): string {
  return input.trim().replace(/[<>]/g, '');
}

function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function validatePassword(password: string): string | null {
  if (password.length < 6) {
    return 'Password must be at least 6 characters';
  }
  if (password.length > 128) {
    return 'Password must be less than 128 characters';
  }
  return null;
}

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const sanitizedEmail = sanitizeInput(email);
    const sanitizedName = sanitizeInput(fullName);

    if (!validateEmail(sanitizedEmail)) {
      setError('Please enter a valid email address');
      return;
    }

    const passwordError = validatePassword(password);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    if (sanitizedName.length < 1 || sanitizedName.length > 100) {
      setError('Name must be between 1 and 100 characters');
      return;
    }

    setLoading(true);

    try {
      await auth.register(sanitizedEmail, password, sanitizedName);
      const data = await auth.login(sanitizedEmail, password);
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        router.push('/dashboard');
      } else {
        setError('Registration successful but login failed. Please login manually.');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Registration failed. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="card auth-card">
        <h1>Create Account</h1>
        
        {error && <div className="alert alert-error">{error}</div>}
        
        <form className="auth-form" onSubmit={handleSubmit}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Full Name</label>
            <input
              type="text"
              className="input"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              maxLength={100}
              pattern="^[a-zA-Z\s]+$"
              title="Only letters and spaces allowed"
            />
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Email</label>
            <input
              type="email"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              maxLength={254}
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
              minLength={6}
              maxLength={128}
              autoComplete="new-password"
            />
          </div>
          
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>
        
        <p className="auth-footer">
          Already have an account? <Link href="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
