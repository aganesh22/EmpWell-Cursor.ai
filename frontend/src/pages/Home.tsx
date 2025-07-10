import React from "react";
import { Link } from "react-router-dom";
import NotificationSystem from "../components/NotificationSystem";

export default function Home() {
  const token = localStorage.getItem("token");

  return (
    <div className="min-h-screen bg-gradient-to-br from-bg-primary to-bg-secondary">
      <main className="container mx-auto flex flex-col items-center justify-center h-screen fade-in">
        <div className="text-center mb-8">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-accent-primary to-accent-secondary bg-clip-text text-transparent">
            Corporate Wellbeing Platform
          </h1>
          <p className="text-xl text-secondary max-w-2xl mx-auto">
            Comprehensive mental health and personality assessment tools for your organization
          </p>
        </div>
        
        {token ? (
          <div className="card max-w-4xl w-full">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold text-primary mb-0">Welcome back!</h2>
              <NotificationSystem userId={1} isAdmin={true} />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Link to="/resources" className="btn btn-primary">
                📚 Resources
              </Link>
              <Link to="/tests" className="btn btn-secondary">
                🧠 Test Library
              </Link>
              <Link to="/test/who5" className="btn btn-outline">
                ❤️ WHO-5 Wellbeing
              </Link>
              <Link to="/test/mbti" className="btn btn-outline">
                🎭 MBTI Personality
              </Link>
              <Link to="/test/disc" className="btn btn-outline">
                🎯 DISC Assessment
              </Link>
              <Link to="/admin/dashboard" className="btn btn-secondary">
                📊 Analytics Dashboard
              </Link>
            </div>
          </div>
        ) : (
          <div className="card max-w-md w-full text-center">
            <h2 className="text-2xl font-semibold mb-4">Get Started</h2>
            <p className="text-secondary mb-6">
              Access our comprehensive wellbeing assessment tools
            </p>
            <div className="flex gap-4">
              <Link to="/login" className="btn btn-primary flex-1">
                Sign In
              </Link>
              <Link to="/register" className="btn btn-outline flex-1">
                Register
              </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}