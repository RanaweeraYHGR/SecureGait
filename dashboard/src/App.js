import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './Dashboard';
import Profile from './Profile';
import Admin from './Admin';
import UpdateUser from './UpdateUser';
import './Premium.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="main-nav">
          <div className="nav-logo">
            <img src="https://ftioxcgnobztqbuyhihc.supabase.co/storage/v1/object/public/user-profiles//logo.jpg" alt="logo" />
          </div>
          <div className="nav-links">
            <Link to="/">Dashboard</Link>
            <Link to="/admin">Admin</Link>
          </div>
        </nav>
        <div className="premium-container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/profile/:name" element={<Profile />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/update-user/:userId" element={<UpdateUser />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
