import React from "react";
import { Link, useNavigate } from "react-router-dom";

interface NavigationProps {
  title?: string;
  showBackButton?: boolean;
  showLogout?: boolean;
}

export default function Navigation({ 
  title = "Corporate Wellbeing Platform", 
  showBackButton = false, 
  showLogout = false 
}: NavigationProps) {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  const handleBack = () => {
    navigate(-1);
  };

  return (
    <nav className="nav container">
      <div className="flex items-center gap-4">
        {showBackButton && (
          <button
            onClick={handleBack}
            className="btn btn-secondary btn-sm"
            aria-label="Go back"
          >
            ← Back
          </button>
        )}
        <Link to="/" className="nav-brand text-decoration-none">
          {title}
        </Link>
      </div>
      
      <div className="nav-links">
        {token ? (
          <>
            <Link to="/tests" className="nav-link">
              Tests
            </Link>
            <Link to="/resources" className="nav-link">
              Resources
            </Link>
            <Link to="/admin/dashboard" className="nav-link">
              Analytics
            </Link>
            {showLogout && (
              <button
                onClick={handleLogout}
                className="btn btn-outline btn-sm"
              >
                Sign Out
              </button>
            )}
          </>
        ) : (
          <>
            <Link to="/login" className="nav-link">
              Sign In
            </Link>
            <Link to="/register" className="btn btn-primary btn-sm">
              Get Started
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}

// Also create a simple page wrapper component
export function PageWrapper({ 
  children, 
  title, 
  showBackButton = false,
  showLogout = true,
  className = "" 
}: {
  children: React.ReactNode;
  title?: string;
  showBackButton?: boolean;
  showLogout?: boolean;
  className?: string;
}) {
  return (
    <div className={`min-h-screen bg-gradient-to-br from-bg-primary to-bg-secondary ${className}`}>
      <Navigation 
        title={title} 
        showBackButton={showBackButton} 
        showLogout={showLogout} 
      />
      <main className="container mx-auto py-8 fade-in">
        {children}
      </main>
    </div>
  );
}