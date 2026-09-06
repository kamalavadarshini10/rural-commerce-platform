import { useState, useEffect } from 'react';
import { apiCall } from '../services/api';
import { CheckCircle, Edit } from 'lucide-react';

export default function CustomerDashboard({ user }) {
  const [data, setData] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [updatedContent, setUpdatedContent] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchInstructions();
  }, []);

  const fetchInstructions = async () => {
    try {
      const res = await apiCall(`/instructions/customer/${user.customer_id}`);
      setData(res);
    } catch (e) {
      console.error(e);
    }
  };

  const handleConfirm = async (isCorrect) => {
    try {
      await apiCall(`/customer-confirmations`, 'POST', {
        instruction_id: data.instruction_id,
        is_correct: isCorrect,
        updated_content: isCorrect ? '' : updatedContent
      });
      setMessage(isCorrect
        ? 'Thank you! Your feedback has been recorded — instructions marked HIGH confidence.'
        : 'Thanks — a new instruction version has been saved and will be reused for future deliveries.');
      setIsEditing(false);
      fetchInstructions();
    } catch (e) {
      setMessage('Error updating instructions.');
    }
  };

  if (!data) return <div>Loading...</div>;

  return (
    <div className="card">
      <h2 className="card-title">Welcome, {user.username}</h2>
      
      {message && <div className="status-badge online mb-4">{message}</div>}

      {!data.has_instructions ? (
        <p>You have an upcoming delivery, but no access instructions are saved.</p>
      ) : (
        <div>
          <p className="mb-2"><strong>Saved Access Instructions:</strong></p>
          <div className="card" style={{backgroundColor: '#f8fafc', padding: '1rem'}}>
            <p>{data.content}</p>
          </div>
          
          <p className="mt-4 mb-2">Are these instructions still correct?</p>
          
          {!isEditing ? (
            <div style={{display: 'flex', gap: '1rem'}}>
              <button className="btn btn-success" onClick={() => handleConfirm(true)}>
                <CheckCircle size={16}/> Yes, Confirm
              </button>
              <button className="btn btn-outline" onClick={() => setIsEditing(true)}>
                <Edit size={16}/> No, Update
              </button>
            </div>
          ) : (
            <div className="mt-2">
              <textarea 
                className="input-field" 
                rows="3"
                value={updatedContent}
                onChange={(e) => setUpdatedContent(e.target.value)}
                placeholder="Enter correct instructions..."
              ></textarea>
              <div style={{display: 'flex', gap: '1rem'}}>
                <button className="btn btn-primary" onClick={() => handleConfirm(false)}>
                  Save New Instructions
                </button>
                <button className="btn btn-outline" onClick={() => setIsEditing(false)}>
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
