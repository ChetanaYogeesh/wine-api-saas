'use client';

import { Suspense } from 'react';
import ForgotPasswordContent from './ForgotPasswordContent';

function Loading() {
  return (
    <div className="auth-page">
      <div className="card auth-card">
        <p>Loading...</p>
      </div>
    </div>
  );
}

export default function ForgotPasswordPage() {
  return (
    <Suspense fallback={<Loading />}>
      <ForgotPasswordContent />
    </Suspense>
  );
}
