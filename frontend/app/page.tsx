import Link from 'next/link';
import './globals.css';

export default function Home() {
  return (
    <>
      <nav className="navbar">
        <div className="container">
          <Link href="/" className="navbar-brand">🍷 Wine API</Link>
          <div className="navbar-nav">
            <Link href="/login">Login</Link>
            <Link href="/register" className="btn btn-primary">Get Started</Link>
          </div>
        </div>
      </nav>

      <section className="hero">
        <div className="container">
          <h1>The Wine Data API for Developers</h1>
          <p>
            Access 32,780+ wine ratings, tasting notes, and regional data 
            with a simple REST API. Perfect for wine apps, recommendation engines, and more.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <Link href="/register" className="btn btn-primary">Start Free</Link>
            <Link href="#pricing" className="btn btn-secondary">View Pricing</Link>
          </div>
        </div>
      </section>

      <section className="features">
        <div className="container">
          <h2>Why Wine API?</h2>
          <div className="features-grid">
            <div className="card feature-card">
              <div className="feature-icon">📊</div>
              <h3>Rich Data</h3>
              <p>32,780+ wines with ratings, tasting notes, regions, and varieties</p>
            </div>
            <div className="card feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Fast & Reliable</h3>
              <p>99.9% uptime with global CDN caching and optimized queries</p>
            </div>
            <div className="card feature-card">
              <div className="feature-icon">🔍</div>
              <h3>Powerful Search</h3>
              <p>Full-text search across wine names and tasting notes</p>
            </div>
            <div className="card feature-card">
              <div className="feature-icon">📈</div>
              <h3>Usage Analytics</h3>
              <p>Track API usage with detailed analytics dashboard</p>
            </div>
            <div className="card feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Secure</h3>
              <p>API key authentication with rate limiting</p>
            </div>
            <div className="card feature-card">
              <div className="feature-icon">💰</div>
              <h3>Free Tier</h3>
              <p>1,000 API calls/month free. Upgrade when you need more.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="pricing" id="pricing">
        <div className="container">
          <h2>Simple, Transparent Pricing</h2>
          <div className="pricing-grid">
            <div className="pricing-card">
              <h3>Free</h3>
              <div className="pricing-price">$0</div>
              <p>Forever free</p>
              <ul className="pricing-features">
                <li>✓ 1,000 API calls/month</li>
                <li>✓ 60 requests/minute</li>
                <li>✓ Basic search</li>
                <li>✓ Email support</li>
              </ul>
              <Link href="/register" className="btn btn-secondary" style={{ width: '100%' }}>Get Started</Link>
            </div>
            <div className="pricing-card featured">
              <span className="tier-badge tier-pro" style={{ marginBottom: '0.5rem' }}>Most Popular</span>
              <h3>Pro</h3>
              <div className="pricing-price">$29</div>
              <p>per month</p>
              <ul className="pricing-features">
                <li>✓ 50,000 API calls/month</li>
                <li>✓ 300 requests/minute</li>
                <li>✓ Advanced search</li>
                <li>✓ Priority support</li>
              </ul>
              <Link href="/register?tier=pro" className="btn btn-primary" style={{ width: '100%' }}>Start Pro Trial</Link>
            </div>
            <div className="pricing-card">
              <h3>Enterprise</h3>
              <div className="pricing-price">$99</div>
              <p>per month</p>
              <ul className="pricing-features">
                <li>✓ 1,000,000 API calls/month</li>
                <li>✓ 1,000 requests/minute</li>
                <li>✓ Custom integrations</li>
                <li>✓ Dedicated support</li>
              </ul>
              <Link href="/register?tier=enterprise" className="btn btn-secondary" style={{ width: '100%' }}>Contact Sales</Link>
            </div>
          </div>
        </div>
      </section>

      <footer style={{ background: '#1f2937', color: 'white', padding: '3rem 0', textAlign: 'center' }}>
        <div className="container">
          <p>&copy; 2026 Wine API. Built with FastAPI.</p>
        </div>
      </footer>
    </>
  );
}
