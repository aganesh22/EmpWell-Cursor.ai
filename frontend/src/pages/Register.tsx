import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { registerUser } from "../lib/api";

export default function Register() {
  const navigate = useNavigate();
  const mutation = useMutation({
    mutationFn: registerUser,
    onSuccess: () => {
      navigate("/login");
    },
  });

  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    mutation.mutate({ email, full_name: fullName, password });
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-bg-primary to-bg-secondary">
      <main className="card max-w-md w-full mx-4 fade-in">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold mb-2">Create Account</h2>
          <p className="text-secondary">Join our wellbeing platform</p>
        </div>
        
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input 
              type="email" 
              required 
              value={email} 
              onChange={(e) => setEmail(e.target.value)}
              className="form-input"
              placeholder="Enter your email"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input 
              type="text" 
              value={fullName} 
              onChange={(e) => setFullName(e.target.value)}
              className="form-input"
              placeholder="Enter your full name"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input 
              type="password" 
              required 
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              className="form-input"
              placeholder="Create a password"
            />
          </div>
          <button type="submit" disabled={mutation.isPending} className="btn btn-primary w-full">
            {mutation.isPending ? (
              <>
                <div className="loading-spinner"></div>
                Creating account...
              </>
            ) : (
              "Create Account"
            )}
          </button>
        </form>
        
        {mutation.isError && <p className="text-error mb-4 text-center">Registration failed</p>}
        
        <div className="text-center pt-6 border-t border-primary">
          <p className="text-secondary mb-0">
            Already have an account? <Link to="/login" className="text-accent-primary hover:text-accent-primary-hover">Sign in</Link>
          </p>
        </div>
      </main>
    </div>
  );
}