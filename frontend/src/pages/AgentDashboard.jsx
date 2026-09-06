import { useState, useEffect } from 'react';
import { apiCall } from '../services/api';
import { Wifi, WifiOff, MapPin, AlertCircle, CheckCircle, XCircle, ShieldCheck, RefreshCw } from 'lucide-react';

// "Incorrect access instructions" failure reason id from FailureReasons seed data.
const INCORRECT_INSTRUCTIONS_REASON_ID = 4;

export default function AgentDashboard({ user }) {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [manualOfflineOverride, setManualOfflineOverride] = useState(false);
  const [deliveries, setDeliveries] = useState([]);
  const [selectedDelivery, setSelectedDelivery] = useState(null);
  const [instruction, setInstruction] = useState(null);
  const [reasons, setReasons] = useState([]);
  const [syncQueue, setSyncQueue] = useState(JSON.parse(localStorage.getItem('syncQueue')) || []);
  const [syncStatus, setSyncStatus] = useState('SYNCED'); // SYNCED | SYNC_PENDING | SYNCING
  const [verified, setVerified] = useState(false);
  const [manualDeliveryPicker, setManualDeliveryPicker] = useState(false);

  const [outcomeState, setOutcomeState] = useState({
    outcome: '',
    reason_id: '',
    note: '',
    new_instruction: ''
  });

  const effectiveOnline = isOnline && !manualOfflineOverride;

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    fetchData();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    setSyncStatus(syncQueue.length > 0 ? 'SYNC_PENDING' : 'SYNCED');
  }, [syncQueue]);

  useEffect(() => {
    if (effectiveOnline && syncQueue.length > 0) {
      syncOfflineData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [effectiveOnline]);

  const fetchData = async () => {
    try {
      if (effectiveOnline) {
        const [delRes, reasonRes] = await Promise.all([
          apiCall(`/deliveries?agent_id=${user.id}`),
          apiCall('/deliveries/failure-reasons')
        ]);
        setDeliveries(delRes);
        setReasons(reasonRes);
        localStorage.setItem('cached_deliveries', JSON.stringify(delRes));
        localStorage.setItem('cached_reasons', JSON.stringify(reasonRes));
      } else {
        setDeliveries(JSON.parse(localStorage.getItem('cached_deliveries')) || []);
        setReasons(JSON.parse(localStorage.getItem('cached_reasons')) || []);
      }
    } catch (e) {
      setDeliveries(JSON.parse(localStorage.getItem('cached_deliveries')) || []);
      setReasons(JSON.parse(localStorage.getItem('cached_reasons')) || []);
    }
  };

  const syncOfflineData = async () => {
    setSyncStatus('SYNCING');
    try {
      const items = syncQueue.map(item => ({
        type: 'delivery_outcome',
        delivery_id: item.delivery_id,
        payload: item.payload
      }));
      const result = await apiCall('/sync', 'POST', items);
      if (result.success) {
        setSyncQueue([]);
        localStorage.setItem('syncQueue', JSON.stringify([]));
        setSyncStatus('SYNCED');
      } else {
        // Keep only the ones that failed to sync
        const failedIds = new Set((result.failed || []).map(f => f.delivery_id));
        const remaining = syncQueue.filter(item => failedIds.has(item.delivery_id));
        setSyncQueue(remaining);
        localStorage.setItem('syncQueue', JSON.stringify(remaining));
        setSyncStatus(remaining.length > 0 ? 'SYNC_PENDING' : 'SYNCED');
      }
      fetchData();
    } catch (e) {
      console.error('Sync failed', e);
      setSyncStatus('SYNC_PENDING');
    }
  };

  const handleSelectDelivery = async (d) => {
    setSelectedDelivery(d);
    setOutcomeState({ outcome: '', reason_id: '', note: '', new_instruction: '' });
    setVerified(false);
    setManualDeliveryPicker(false);

    try {
      if (effectiveOnline) {
        const inst = await apiCall(`/deliveries/${d.id}/instructions`);
        setInstruction(inst);
        localStorage.setItem(`inst_${d.id}`, JSON.stringify(inst));
      } else {
        setInstruction(JSON.parse(localStorage.getItem(`inst_${d.id}`)) || null);
      }
    } catch (e) {
      setInstruction(JSON.parse(localStorage.getItem(`inst_${d.id}`)) || null);
    }
  };

  const handleSubmitOutcome = async () => {
    const payload = {
      outcome: outcomeState.outcome,
      reason_id: outcomeState.reason_id ? Number(outcomeState.reason_id) : null,
      note: outcomeState.note,
      new_instruction: outcomeState.new_instruction,
      instruction_id: instruction?.instruction_id,
      instructions_available: instruction?.has_instructions || false,
      instructions_shown: instruction?.has_instructions || false,
      instructions_verified: verified,
      instructions_reused: instruction?.has_instructions && outcomeState.outcome === 'SUCCESS',
      instructions_incorrect: instruction?.has_instructions
        && outcomeState.outcome === 'FAILURE'
        && Number(outcomeState.reason_id) === INCORRECT_INSTRUCTIONS_REASON_ID
    };

    if (effectiveOnline) {
      await apiCall(`/deliveries/${selectedDelivery.id}/outcome`, 'POST', payload);
      fetchData();
      setSelectedDelivery(null);
    } else {
      const newQueue = [...syncQueue, { type: 'delivery_outcome', delivery_id: selectedDelivery.id, payload }];
      setSyncQueue(newQueue);
      localStorage.setItem('syncQueue', JSON.stringify(newQueue));
      const updatedDel = deliveries.filter(d => d.id !== selectedDelivery.id);
      setDeliveries(updatedDel);
      localStorage.setItem('cached_deliveries', JSON.stringify(updatedDel));
      setSelectedDelivery(null);
    }
  };

  const failureSummary = instruction?.failure_summary;
  const hasRepeatFailureWarning = failureSummary?.is_repeat_failure;

  return (
    <div>
      <div className="flex-between mb-4">
        <h2 className="card-title" style={{marginBottom: 0, borderBottom: 'none'}}>My Deliveries</h2>
        <div style={{display: 'flex', gap: '0.5rem', alignItems: 'center'}}>
          <div className={`status-badge ${effectiveOnline ? 'online' : 'offline'}`}>
            {effectiveOnline ? <Wifi size={14} /> : <WifiOff size={14} />}
            {effectiveOnline ? 'ONLINE' : 'OFFLINE'}
          </div>
          {syncStatus === 'SYNC_PENDING' && (
            <div className="status-badge sync-pending">SYNC PENDING ({syncQueue.length})</div>
          )}
          {syncStatus === 'SYNCING' && (
            <div className="status-badge sync-pending"><RefreshCw size={12} className="spin" /> SYNCING</div>
          )}
          {isOnline && (
            <button
              className="btn btn-outline"
              style={{padding: '0.25rem 0.5rem', fontSize: '0.7rem'}}
              onClick={() => setManualOfflineOverride(!manualOfflineOverride)}
              title="Simulate offline mode for the demo"
            >
              {manualOfflineOverride ? 'Go Online' : 'Simulate Offline'}
            </button>
          )}
        </div>
      </div>

      {!selectedDelivery ? (
        <ul className="delivery-list">
          {deliveries.length === 0 ? <p className="text-muted">No pending deliveries.</p> : null}
          {deliveries.map(d => (
            <li key={d.id} className="delivery-item" onClick={() => handleSelectDelivery(d)}>
              <div className="flex-between">
                <strong>{d.customer_name}</strong>
                <span className="text-sm text-muted">ID: {d.id}</span>
              </div>
              <div className="text-sm text-muted mt-2 flex items-center gap-2">
                <MapPin size={14} /> {d.basic_address}
              </div>
              {!d.gps_available && (
                <div className="text-sm mt-2" style={{color: 'var(--warning-color)'}}>
                  <AlertCircle size={14} style={{display:'inline', marginRight:'4px'}}/>
                  GPS Unavailable
                </div>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <div className="card">
          <button className="btn btn-outline mb-4" onClick={() => setSelectedDelivery(null)}>← Back</button>

          <h3 className="card-title">Delivery #{selectedDelivery.id}</h3>
          <p><strong>Customer:</strong> {selectedDelivery.customer_name} ({selectedDelivery.phone})</p>
          <p><strong>Address:</strong> {selectedDelivery.basic_address}</p>
          <p><strong>Landmark:</strong> {selectedDelivery.landmark}</p>

          {!selectedDelivery.gps_available && (
            <div className="status-badge sync-pending mt-2 mb-2">
              GPS Unavailable — Manual location selection &amp; landmark-based navigation (simulated fallback)
            </div>
          )}

          {hasRepeatFailureWarning && (
            <div className="card mt-2 mb-2" style={{backgroundColor: '#fef2f2', border: '1px solid var(--danger-color)'}}>
              <strong style={{color: 'var(--danger-color)'}}>
                <AlertCircle size={14} style={{display:'inline', marginRight:'4px'}}/>
                Repeat-Failure Location
              </strong>
              <p className="text-sm mt-2">
                {failureSummary.failures} of {failureSummary.attempts} previous attempt(s) failed here.
                {failureSummary.reasons.length > 0 && ` Reasons: ${failureSummary.reasons.join(', ')}.`}
              </p>
            </div>
          )}

          {instruction?.has_instructions && (
            <div className="card mt-4" style={{backgroundColor: '#f8fafc', border: '1px solid var(--border-color)'}}>
              <div className="flex-between mb-2">
                <strong>Access Instructions</strong>
                <span className={`confidence-badge ${instruction.confidence.toLowerCase()}`}>
                  {instruction.confidence} CONFIDENCE
                </span>
              </div>
              <p className="text-sm">{instruction.content}</p>
              <p className="text-sm mt-2 text-muted"><em>{instruction.reason}</em></p>

              {!verified ? (
                <button
                  className="btn btn-outline mt-2"
                  style={{fontSize: '0.75rem', padding: '0.35rem 0.6rem'}}
                  onClick={() => setVerified(true)}
                >
                  <ShieldCheck size={14} style={{display:'inline', marginRight:'4px'}} /> Verify Instructions On-Site
                </button>
              ) : (
                <div className="text-sm mt-2" style={{color: 'var(--success-color)'}}>
                  <CheckCircle size={14} style={{display:'inline', marginRight:'4px'}} /> Marked as verified for this delivery
                </div>
              )}
            </div>
          )}

          {!instruction?.has_instructions && (
            <div className="card mt-4" style={{backgroundColor: '#fffbeb', border: '1px solid var(--warning-color)'}}>
              <p className="text-sm">No access instructions captured yet for this location. Please add what you find below after delivery.</p>
            </div>
          )}

          <div className="mt-4">
            <h4>Record Outcome</h4>
            <div className="flex gap-2 mt-2" style={{display: 'flex', gap: '0.5rem'}}>
              <button
                className={`btn ${outcomeState.outcome === 'SUCCESS' ? 'btn-success' : 'btn-outline'}`}
                onClick={() => setOutcomeState({...outcomeState, outcome: 'SUCCESS'})}
              >
                <CheckCircle size={16}/> Success
              </button>
              <button
                className={`btn ${outcomeState.outcome === 'FAILURE' ? 'btn-danger' : 'btn-outline'}`}
                onClick={() => setOutcomeState({...outcomeState, outcome: 'FAILURE'})}
              >
                <XCircle size={16}/> Failure
              </button>
            </div>

            {outcomeState.outcome === 'FAILURE' && (
              <div className="mt-4">
                <label className="label">Reason</label>
                <select
                  className="input-field"
                  value={outcomeState.reason_id}
                  onChange={(e) => setOutcomeState({...outcomeState, reason_id: e.target.value})}
                >
                  <option value="">Select reason...</option>
                  {reasons.map(r => (
                    <option key={r.id} value={r.id}>{r.reason_text}</option>
                  ))}
                </select>
              </div>
            )}

            {outcomeState.outcome && (
              <div className="mt-2">
                <label className="label">Optional Note</label>
                <input
                  type="text"
                  className="input-field"
                  value={outcomeState.note}
                  onChange={(e) => setOutcomeState({...outcomeState, note: e.target.value})}
                  placeholder="Short note..."
                />
              </div>
            )}

            {outcomeState.outcome === 'SUCCESS' && (
              <div className="mt-2">
                <label className="label">Add/Update Instructions (Optional)</label>
                <input
                  type="text"
                  className="input-field"
                  value={outcomeState.new_instruction}
                  onChange={(e) => setOutcomeState({...outcomeState, new_instruction: e.target.value})}
                  placeholder="e.g. Red gate on the left"
                />
              </div>
            )}

            {outcomeState.outcome && (
              <button className="btn btn-primary w-full mt-4" onClick={handleSubmitOutcome}>
                Save Outcome
              </button>
            )}
          </div>
        </div>
      )}

      {!effectiveOnline && (
        <div className="card mt-4" style={{backgroundColor: '#f8fafc'}}>
          <p className="text-sm text-muted">
            Working offline — showing cached deliveries and instructions. Outcomes recorded now
            will be queued and synced automatically once you're back online.
          </p>
        </div>
      )}
    </div>
  );
}
