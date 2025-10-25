'use client';

import React, { useState, useEffect } from 'react';
import { LandingPage } from '../components/LandingPage';
import { AuthPage } from '../components/AuthPage';
import { CustomerDashboard } from '../components/CustomerDashboard';
import { DriverDashboard } from '../components/DriverDashboard';
import { DispatcherDashboard } from '../components/DispatcherDashboard';

type User = {
  id: string;
  email: string;
  role: 'customer' | 'driver' | 'dispatcher';
  name: string;
  token: string;
};

type AppState = 'landing' | 'auth' | 'dashboard';

export default function HomePage() {
  const [appState, setAppState] = useState<AppState>('landing');
  const [user, setUser] = useState<User | null>(null);
  const [selectedRole, setSelectedRole] = useState<'customer' | 'driver' | 'dispatcher' | null>(null);

  // Check for existing session on app load
  useEffect(() => {
    const savedUser = localStorage.getItem('ugunja_user');
    if (savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
        setAppState('dashboard');
      } catch (error) {
        localStorage.removeItem('ugunja_user');
      }
    }
  }, []);

  const handleRoleSelect = (role: 'customer' | 'driver' | 'dispatcher') => {
    setSelectedRole(role);
    setAppState('auth');
  };

  const handleLogin = (userData: User) => {
    console.log('Login successful, user data:', userData); // Debug log
    setUser(userData);
    localStorage.setItem('ugunja_user', JSON.stringify(userData));
    setAppState('dashboard');
    console.log('App state set to dashboard'); // Debug log
  };

  const handleLogout = () => {
    setUser(null);
    setSelectedRole(null);
    localStorage.removeItem('ugunja_user');
    setAppState('landing');
  };

  const handleBackToLanding = () => {
    setSelectedRole(null);
    setAppState('landing');
  };

  const renderDashboard = () => {
    if (!user) return null;

    console.log('Rendering dashboard for user:', user);

    const roleLower = user.role.toLowerCase();
    console.log('Role after toLowerCase:', roleLower);
    
    switch (roleLower) {
      case 'customer':
        return <CustomerDashboard user={user} onLogout={handleLogout} />;
      case 'driver':
        return <DriverDashboard user={user} onLogout={handleLogout} />;
      case 'dispatcher':
        return <DispatcherDashboard user={user} onLogout={handleLogout} />;
      default:
        console.log('Unknown role:', user.role);
        return <div className="p-8 text-center">
          <h2 className="text-2xl font-bold mb-4">Unknown Role: {user.role}</h2>
          <button onClick={handleLogout} className="mt-4 px-4 py-2 bg-red-500 text-white rounded">
            Logout
          </button>
        </div>;
    }
  };

  return (
    <>
      {appState === 'landing' && (
        <LandingPage onRoleSelect={handleRoleSelect} />
      )}
      {appState === 'auth' && selectedRole && (
        <AuthPage 
          selectedRole={selectedRole}
          onLogin={handleLogin} 
          onBack={handleBackToLanding} 
        />
      )}
      {appState === 'dashboard' && renderDashboard()}
    </>
  );
}