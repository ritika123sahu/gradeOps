import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';
import TADashboard from './pages/TADashboard';
import InstructorUpload from './pages/InstructorUpload';
import Login from './pages/Login';

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));

  const handleLogin = (newToken: string) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route 
          path="/ta" 
          element={token ? <TADashboard /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/instructor" 
          element={token ? <InstructorUpload /> : <Navigate to="/login" />} 
        />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;
