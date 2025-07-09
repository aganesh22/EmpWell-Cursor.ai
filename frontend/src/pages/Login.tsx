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
    <main style={{ maxWidth: 400, margin: "2rem auto" }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Email</label>
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div style={{ marginTop: 12 }}>
          <label>Password</label>
          <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <button type="submit" disabled={mutation.isPending} style={{ marginTop: 16 }}>
          {mutation.isPending ? "Logging in..." : "Login"}
        </button>
      </form>
      {mutation.isError && <p style={{ color: "red" }}>Invalid credentials</p>}
      {googleMutation.isError && <p style={{ color: "red" }}>Google sign-in failed</p>}
      {azureMutation.isError && <p style={{ color: "red" }}>Azure AD sign-in failed</p>}
      
      <div style={{ marginTop: 20, textAlign: 'center' }}>
        <div style={{ margin: '16px 0', fontSize: '14px', color: '#666' }}>or sign in with</div>
        
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          {/* Google Sign-In */}
          <div ref={googleButtonRef} style={{ minHeight: '40px' }}>
            {isGoogleLoading && <p style={{ margin: 0, padding: '8px' }}>Signing in with Google...</p>}
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
              style={{
                padding: '8px 16px',
                border: '1px solid #0078d4',
                borderRadius: '4px',
                backgroundColor: '#0078d4',
                color: 'white',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                minWidth: '160px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              {isAzureLoading ? (
                'Signing in...'
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
      
      <p style={{ marginTop: 16 }}>
        Don't have an account? <Link to="/register">Register</Link>
      </p>
    </main>
  );
}