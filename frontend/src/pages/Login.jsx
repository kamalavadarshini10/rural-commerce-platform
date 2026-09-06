import { useState } from 'react';
import { apiCall } from '../services/api';

const DEMO_ACCOUNTS = [
  { label: 'Agent', username: 'agent@example.com', password: 'agent123' },
  { label: 'Customer', username: 'customer@example.com', password: 'customer123' },
  { label: 'Admin', username: 'admin@example.com', password: 'admin123' },
];

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const user = await apiCall('/auth/login', 'POST', { username, password });
      onLogin(user);
    } catch (err) {
      setError('Invalid credentials. Try one of the demo accounts below.');
    }
  };

  const fillDemo = (acc) => {
    setUsername(acc.username);
    setPassword(acc.password);
    setError('');
  };

  return (
    <div className="login-container">
      <div className="card login-card">
        <h2 className="card-title text-center" style={{color: 'var(--primary-color)'}}>RuralRoute</h2>
        <p className="text-center text-muted mb-4 text-sm">Rural Delivery Access Instruction Capture &amp; Reuse</p>

        {error && <div className="mb-4 text-sm" style={{color: 'var(--danger-color)'}}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <label className="label">Username</label>
          <input
            type="text"
            className="input-field"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="e.g. agent@example.com"
          />
          <label className="label mt-2">Password</label>
          <input
            type="password"
            className="input-field"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
          />
          <button type="submit" className="btn btn-primary w-full mt-2">Login</button>
        </form>

        <div className="mt-4 text-xs text-muted">
          <strong>Demo Accounts</strong> (tap to fill):
          <div style={{display: 'flex', gap: '0.5rem', marginTop: '0.5rem', flexWrap: 'wrap'}}>
            {DEMO_ACCOUNTS.map((acc) => (
              <button
                type="button"
                key={acc.username}
                className="btn btn-outline"
                style={{padding: '0.25rem 0.5rem', fontSize: '0.75rem'}}
                onClick={() => fillDemo(acc)}
              >
                {acc.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
