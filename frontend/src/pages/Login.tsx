import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock } from 'lucide-react';

interface LoginProps {
  onLogin: (token: string) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('ta'); // For navigation only
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    try {
      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        onLogin(data.access_token);
        if (role === 'instructor') navigate('/instructor');
        else navigate('/ta');
      } else {
        const err = await response.json();
        setError(err.detail || 'Login failed');
      }
    } catch (err) {
      setError('Connection error. Is the backend running?');
    }
  };

  return (
    <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', width: '100%'}}>
      <div style={{background: '#2a2a2a', padding: '40px', borderRadius: '12px', width: '350px'}}>
        <h2 style={{textAlign: 'center', marginBottom: '30px'}}><Lock style={{marginRight: 10}}/> GradeOps Login</h2>
        
        {error && <div style={{color: '#ef4444', marginBottom: '15px', fontSize: '0.9rem'}}>{error}</div>}
        
        <form onSubmit={handleSubmit} style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
          <input 
            type="email" 
            placeholder="Email (e.g. instructor@test.com)" 
            style={{padding: '12px', borderRadius: '6px', background: '#333', border: '1px solid #444', color: 'white'}}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input 
            type="password" 
            placeholder="Password (password123)" 
            style={{padding: '12px', borderRadius: '6px', background: '#333', border: '1px solid #444', color: 'white'}}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <select 
            style={{padding: '12px', borderRadius: '6px', background: '#333', border: '1px solid #444', color: 'white'}}
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            <option value="ta">Teaching Assistant</option>
            <option value="instructor">Instructor</option>
          </select>
          <button type="submit" className="button button-primary" style={{marginTop: '10px'}}>Login</button>
        </form>
        <p style={{marginTop: '20px', fontSize: '0.8rem', color: '#888', textAlign: 'center'}}>
          Demo Creds: instructor@test.com / password123
        </p>
      </div>
    </div>
  );
};

export default Login;
