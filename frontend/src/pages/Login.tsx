/// <reference types="vite/client" />
import React, { useState, useEffect, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { loginUser, loginWithGoogle, loginWithAzure } from "../lib/api";
import { GoogleAuth } from "../lib/google-auth";
import { AzureAuth } from "../lib/azure-auth";

export default function Login() {
  const navigate = useNavigate();
  const googleButtonRef = useRef<HTMLDivElement>(null);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isAzureLoading, setIsAzureLoading] = useState(false);

  const mutation = useMutation({
    mutationFn: loginUser,
    onSuccess: (data) => {
      localStorage.setItem("token", data.data.access_token);
      navigate("/");
    },
  });

  const googleMutation = useMutation({
    mutationFn: loginWithGoogle,
    onSuccess: (data) => {
      localStorage.setItem("token", data.data.access_token);
      setIsGoogleLoading(false);
      navigate("/");
    },
    onError: () => {
      setIsGoogleLoading(false);
    },
  });

  const azureMutation = useMutation({
    mutationFn: loginWithAzure,
    onSuccess: (data) => {
      localStorage.setItem("token", data.data.access_token);
      setIsAzureLoading(false);
      navigate("/");
    },
    onError: () => {
      setIsAzureLoading(false);
    },
  });

  // Enhanced Google SSO setup
  useEffect(() => {
    const setupGoogleAuth = async () => {
      const googleAuth = GoogleAuth.getInstance();
      
      if (!googleAuth.isConfigured()) {
        console.log("Google SSO not configured - skipping");
        return;
      }

      try {
        await googleAuth.initialize();
        
        // Render the Google Sign-In button
        if (googleButtonRef.current) {
          googleAuth.renderSignInButton(googleButtonRef.current, {
            theme: 'outline',
            size: 'large',
            text: 'signin_with',
            shape: 'rectangular',
          });
        }

        // Listen for Google sign-in events
        const handleGoogleSignIn = (event: CustomEvent) => {
          setIsGoogleLoading(true);
          googleMutation.mutate(event.detail.credential);
        };

        window.addEventListener('google-signin', handleGoogleSignIn as EventListener);
        
        return () => {
          window.removeEventListener('google-signin', handleGoogleSignIn as EventListener);
        };
      } catch (error) {
        console.error("Failed to initialize Google Auth:", error);
      }
    };

    setupGoogleAuth();

    // Setup Azure AD authentication
    const setupAzureAuth = async () => {
      const azureAuth = AzureAuth.getInstance();
      
      if (!azureAuth.isConfigured()) {
        console.log("Azure AD SSO not configured - skipping");
        return;
      }

      try {
        await azureAuth.initialize();

        // Listen for Azure sign-in events
        const handleAzureSignIn = async (event: Event) => {
          const customEvent = event as CustomEvent;
          setIsAzureLoading(true);
          azureMutation.mutate(customEvent.detail.accessToken);
        };

        window.addEventListener('azure-auth-success', handleAzureSignIn);
        
        return () => {
          window.removeEventListener('azure-auth-success', handleAzureSignIn);
        };
      } catch (error) {
        console.error("Failed to initialize Azure Auth:", error);
      }
    };

    setupAzureAuth();
  }, [googleMutation, azureMutation]);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    mutation.mutate({ email, password });
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-bg-primary to-bg-secondary">
      <main className="card max-w-md w-full mx-4 fade-in">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold mb-2">Welcome Back</h2>
          <p className="text-secondary">Sign in to your account</p>
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
            <label className="form-label">Password</label>
            <input 
              type="password" 
              required 
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              className="form-input"
              placeholder="Enter your password"
            />
          </div>
          <button type="submit" disabled={mutation.isPending} className="btn btn-primary w-full">
            {mutation.isPending ? (
              <>
                <div className="loading-spinner"></div>
                Signing in...
              </>
            ) : (
              "Sign In"
            )}
          </button>
        </form>
        
        {mutation.isError && <p className="text-error mb-4 text-center">Invalid credentials</p>}
        {googleMutation.isError && <p className="text-error mb-4 text-center">Google sign-in failed</p>}
        {azureMutation.isError && <p className="text-error mb-4 text-center">Azure AD sign-in failed</p>}
        
        <div className="text-center">
          <div className="text-sm text-muted mb-4">or sign in with</div>
          
          <div className="flex gap-3 justify-center flex-wrap">
            {/* Google Sign-In */}
            <div ref={googleButtonRef} className="min-h-10">
              {isGoogleLoading && (
                <div className="flex items-center gap-2 p-2 text-sm">
                  <div className="loading-spinner"></div>
                  Signing in with Google...
                </div>
              )}
            </div>
            
            {/* Azure AD Sign-In */}
            {AzureAuth.getInstance().isConfigured() && (
              <button
                onClick={async () => {
                  setIsAzureLoading(true);
                  try {
                    await AzureAuth.getInstance().loginPopup();
                  } catch (error) {
                    setIsAzureLoading(false);
                    console.error('Azure login failed:', error);
                  }
                }}
                disabled={isAzureLoading}
                className="btn btn-outline btn-sm"
              >
                {isAzureLoading ? (
                  <>
                    <div className="loading-spinner"></div>
                    Signing in...
                  </>
                ) : (
                  <>
                    <span>🏢</span>
                    <span>Sign in with Microsoft</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
        
        <div className="text-center mt-6 pt-6 border-t border-primary">
          <p className="text-secondary mb-0">
            Don't have an account? <Link to="/register" className="text-accent-primary hover:text-accent-primary-hover">Create one</Link>
          </p>
        </div>
      </main>
    </div>
  );
}