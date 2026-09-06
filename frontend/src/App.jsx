import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import AgentDashboard from './pages/AgentDashboard';
import CustomerDashboard from './pages/CustomerDashboard';
import AdminDashboard from './pages/AdminDashboard';
import { useState } from 'react';

function App() {
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')) || null);

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  return (
    <BrowserRouter>
      <div className="app-container">
        {user && (
          <header className="app-header">
            <div className="brand">RuralRoute</div>
            <div className="user-info">
              <span>{user.username} ({user.role})</span>
              <button onClick={handleLogout} className="btn btn-outline" style={{padding: '0.25rem 0.5rem', fontSize: '0.75rem'}}>Logout</button>
            </div>
          </header>
        )}
        <Routes>
          <Route path="/login" element={!user ? <Login onLogin={handleLogin} /> : <Navigate to="/" />} />
          
          <Route path="/" element={
            !user ? <Navigate to="/login" /> :
            user.role === 'agent' ? <AgentDashboard user={user} /> :
            user.role === 'admin' ? <AdminDashboard user={user} /> :
            user.role === 'customer' ? <CustomerDashboard user={user} /> :
            <div>Invalid Role</div>
          } />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
