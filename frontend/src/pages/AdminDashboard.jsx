import { useState, useEffect } from 'react';
import { apiCall } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [repeatFailures, setRepeatFailures] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const statsRes = await apiCall('/admin/analytics');
        const failuresRes = await apiCall('/admin/repeat-failures');
        setStats(statsRes);
        setRepeatFailures(failuresRes);
      } catch (e) {
        console.error(e);
      }
    };
    fetchData();
  }, []);

  if (!stats) return <div>Loading...</div>;

  const chartData = [
    { name: 'Deliveries', Success: stats.successful_deliveries, Failed: stats.failed_deliveries }
  ];

  return (
    <div>
      <h2 className="card-title">Admin Dashboard</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Deliveries</div>
          <div className="stat-value">{stats.total_deliveries}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Success Rate</div>
          <div className="stat-value" style={{color: 'var(--success-color)'}}>
            {stats.total_deliveries ? Math.round((stats.successful_deliveries / stats.total_deliveries) * 100) : 0}%
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Repeat-Failure Locations</div>
          <div className="stat-value" style={{color: 'var(--danger-color)'}}>{stats.repeat_failure_location_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Instructions Reused</div>
          <div className="stat-value" style={{color: 'var(--primary-color)'}}>{stats.instruction_reuse_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Customer Confirmations</div>
          <div className="stat-value" style={{color: 'var(--warning-color)'}}>{stats.customer_confirmation_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Customer Updates</div>
          <div className="stat-value" style={{color: 'var(--warning-color)'}}>{stats.customer_update_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Low-Confidence Instructions</div>
          <div className="stat-value" style={{color: 'var(--danger-color)'}}>{stats.low_confidence_instruction_count}</div>
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">Success vs Failure</h3>
        <div style={{height: '300px'}}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Bar dataKey="Success" fill="var(--success-color)" />
              <Bar dataKey="Failed" fill="var(--danger-color)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">Repeat Failure Locations</h3>
        {repeatFailures.length === 0 ? (
          <p className="text-muted">No repeat failures detected.</p>
        ) : (
          <div style={{overflowX: 'auto'}}>
            <table style={{width: '100%', textAlign: 'left', borderCollapse: 'collapse'}}>
              <thead>
                <tr style={{borderBottom: '1px solid var(--border-color)'}}>
                  <th style={{padding: '0.5rem'}}>Location</th>
                  <th style={{padding: '0.5rem'}}>Attempts</th>
                  <th style={{padding: '0.5rem'}}>Failures</th>
                  <th style={{padding: '0.5rem'}}>Reasons</th>
                  <th style={{padding: '0.5rem'}}>Latest Instructions</th>
                  <th style={{padding: '0.5rem'}}>Confidence</th>
                  <th style={{padding: '0.5rem'}}>Reused?</th>
                </tr>
              </thead>
              <tbody>
                {repeatFailures.map(f => (
                  <tr key={f.location_id} style={{borderBottom: '1px solid var(--border-color)'}}>
                    <td style={{padding: '0.5rem'}}>
                      <strong>{f.address}</strong>
                      <div className="text-xs text-muted">{f.landmark}</div>
                    </td>
                    <td style={{padding: '0.5rem'}}>{f.attempts}</td>
                    <td style={{padding: '0.5rem'}}>
                      <span className="status-badge offline">{f.total_failures}</span>
                    </td>
                    <td style={{padding: '0.5rem', fontSize: '0.875rem'}}>{f.reasons.join(', ')}</td>
                    <td style={{padding: '0.5rem', fontSize: '0.875rem'}}>{f.latest_instructions || '—'}</td>
                    <td style={{padding: '0.5rem'}}>
                      {f.instruction_confidence
                        ? <span className={`confidence-badge ${f.instruction_confidence.toLowerCase()}`}>{f.instruction_confidence}</span>
                        : '—'}
                    </td>
                    <td style={{padding: '0.5rem'}}>{f.instructions_reused ? 'Yes' : 'No'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
